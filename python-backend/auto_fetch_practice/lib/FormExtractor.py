import json
import re
from enum import Enum

import requests
from bs4 import BeautifulSoup

# constants
ALL_DATA_FIELDS = "FB_PUBLIC_LOAD_DATA_"
FORM_SESSION_TYPE_ID = 8
ANY_TEXT_FIELD = "ANY TEXT!!"  # Other 的選項
ignored_questions: set[str] = {
    "系所／單位 Department",
    "測驗動機(修讀整合式英語課程之同學請務必填寫正確，勾選錯誤一律不予計分)"
}
""" --------- Helper functions ---------  """


def get_form_response_url(url: str) -> str:
    """
    Convert a Google Form URL to its corresponding form response URL using regex.

    Args:
        url (str): The original Google Form URL.

    Returns:
        str: The modified form response URL.
    """
    # 去除前後空白與末端/
    url = url.strip().rstrip('/')

    # 檢查是否包含 'forms.gle'
    if re.search(re.compile(r'https?://forms\.gle/[\w-]+'), url):
        try:
            # 獲取重定向後的實際 URL
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 確保請求成功
            url = response.url.strip()
        except requests.RequestException as e:
            raise ValueError(f"無法解析 URL: {e}")

    url = re.sub(r'\?usp=.+$', '', url)
    url = re.sub(r'/viewform?$', '/formResponse', url)

    if not re.search(r'/formResponse?$', url):
        url += '/formResponse'

    return url


def extract_script_variables(name: str, html_content: str):
    """ Extract a variable from a script tag in a HTML page """
    pattern = re.compile(r'var\s' + name + r'\s=\s(.*?);</script>')

    match = pattern.search(html_content)
    if not match:
        return None
    value_str = match.group(1)
    return json.loads(value_str)


def get_fb_public_load_data(url: str):
    """ Get form data from a Google form url """
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print("Error! Can't get form data", response.status_code)
        return None
    return extract_script_variables(ALL_DATA_FIELDS, response.text)


# ------ MAIN LOGIC ------ #
def parse_entry(entry):
    entry_name = entry[1]
    entry_type_id = entry[3]

    # FIXED 文字標題跳過
    if entry_type_id == 6:
        return None

    result = []
    for sub_entry in entry[4]:
        info = {
            "id": sub_entry[0],
            "container_name": entry_name,
            "type": entry_type_id,
            "required": sub_entry[2] == 1,
            "name": ' - '.join(sub_entry[3]) if (len(sub_entry) > 3 and sub_entry[3]) else None,
            "options": [(x[0] or ANY_TEXT_FIELD) for x in sub_entry[1]] if sub_entry[1] else None,
        }

        result.append(info)
    return result


def parse_form_entries(url: str):
    """
    In window.FB_PUBLIC_LOAD_DATA_ (as v) 
    - v[1][1] is the form entries array
    - for x in v[1][1]:
        x[0] is the entry id of the entry container
        x[1] is the entry name (*)
        x[3] is the entry type 
        x[4] is the array of entry (usually length of 1, but can be more if Grid Choice, Linear Scale)
            x[4][0] is the entry id (we only need this to make request) (*)
            x[4][1] is the array of entry value (if null then text)
                x[4][1][i][0] is the i-th entry value option (*)
            x[4][2] field required (1 if required, 0 if not) (*)
            x[4][3] name of Grid Choice, Linear Scale (in array)
    - v[1][10][6]: determine the email field if the form request email
        1: Do not collect email
        2: required checkbox, get verified email
        3: required responder input
    """

    url = get_form_response_url(url)
    v = get_fb_public_load_data(url)
    if not v or not v[1] or not v[1][1]:
        print("Error! Can't get form entries. Login may be required.")
        return None

    parsed_entries = []
    page_count = 0
    for entry in v[1][1]:
        if entry[3] == FORM_SESSION_TYPE_ID:
            page_count += 1
            continue

        parsed = parse_entry(entry)
        if parsed:
            parsed_entries += parsed

    if page_count > 0:
        parsed_entries.append({
            "id": "pageHistory",
            "container_name": "Page History",
            "type": -1,
            "required": False,
            "options": None,
            "default_value": ','.join(map(str, range(page_count + 1)))
        })

    # Collect email addresses
    if v[1][10][6] > 1:
        parsed_entries.append({
            "id": "emailAddress",
            "container_name": "Email Address",
            "type": -2,
            "required": True,
            "options": None,
        })

    return parsed_entries


# ------ OUTPUT ------ #
class Output(Enum):
    Return = 0
    Console = 1


def get_form_submit_request(
        url: str,
        output: Output = Output.Return,
):
    """ Get form request body data """
    entries = parse_form_entries(url)
    result = generate_form_request_dict(entries)

    if output == Output.Console:
        print(result)
        return None
    elif output == Output.Return:
        return result
    else:
        return None


class FormType(Enum):
    EmailAddress = -2
    PageHistory = -1
    SHORT_ANSWER = 0
    PARAGRAPH = 1
    MULTIPLE_CHOICE = 2
    DROPDOWN = 3
    CHECKBOXES = 4
    LINEAR_SCALE = 5
    GRID_CHOICE = 7
    DATE = 9
    TIME = 10


def generate_form_request_dict(entries):
    """ Generate a dict of form request data from entries """

    result = dict()
    for entry in entries:
        cur_entry = dict()
        cur_entry['question'] = entry['container_name']
        cur_entry['require'] = entry['required']
        cur_entry['option_type'] = FormType(entry['type'])
        cur_entry['options'] = entry['options']
        cur_entry['value'] = entry.get("default_value", "")
        result[
            f"entry.{entry['id']}" if entry['type'] >= 0 else entry["id"]
        ] = cur_entry

        assert not entry.get('name')  # IDK what it is

    return result


# 透過 HTML 取得正確的答案
def extract_correct_answers(html_content: bytes, mapper: dict[str, str]) -> dict:
    """
    從給定的 HTML 內容中提取答對題目的 entry ID 與對應的答案值。

    :param html_content: 包含 HTML 的字符串
    :param mapper: 問題字符串到 entry_id 的映射字典，例如 {"問題1": "entry.1234567890"}
    :return: 字典形式的 {entry_id: answer_value}
    """
    soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
    correct_answers = {}

    # 找到所有包含問題的區塊，每個問題都在 div class="Qr7Oae"
    question_divs = soup.find_all('div', class_='Qr7Oae', role='listitem')

    for q_div in question_divs:
        # 檢查是否答對
        if not q_div.find('div', attrs={'aria-label': '答對'}): continue

        # 嘗試找到此問題對應的 hidden input，該 input 包含 entry ID 和正確答案值
        if hidden_input := q_div.find('input', {'type': 'hidden', 'name': re.compile(r'^entry\.\d+$')}):
            entry_id = hidden_input.get('name')
            answer_value = hidden_input.get('value')

            if entry_id and answer_value:
                correct_answers[entry_id] = answer_value
            else:
                print(f"警告: 找到的 hidden_input 缺少 name 或 value。")
            continue

        # 提取問題的文字
        if not (question_heading := q_div.find('div', role='heading', attrs={'aria-level': '3'})):
            print("警告: 無法找到問題的 heading div。")
            continue

        if not (question_text_span := question_heading.find('span', class_='M7eMe')):
            print("警告: 無法找到問題文字的 span 元素。")
            continue

        # 由問題文字 mapper 映射 entry_id
        question_text = question_text_span.get_text(strip=True).strip().replace('\n', '')
        entry_id = None
        for k, v in mapper.items():
            if v.strip().rstrip(" (required)") == question_text:
                entry_id = k
                break

        if entry_id is None:
            print(f"警告: mapper 中未找到問題 '{question_text}' 對應的 entry_id。")
            continue

        # 找到選中的選項，通常具有 aria-checked="true"
        selected_option = q_div.find('div', class_='IK9nwb')
        if not selected_option:
            print(f"警告: 在問題 '{question_text}' 中找不到選中的選項。")
            continue

        # 檢查是否能找到正確的 span 元素
        span_element = selected_option.find('span', class_='OIC90c')  # 修正 class_ 名稱，去除多餘空格
        if not span_element:
            print(f"警告: 選中的選項缺少 class 'OIC90c' 的 span 元素。")
            continue

        # 提取 span 中的文字作為答案值
        answer_value = span_element.get_text(strip=True)
        if not answer_value:
            print(f"警告: 選中的選項缺少文字內容。")
            continue

        # 終於拿到答案了 orz...
        correct_answers[entry_id] = answer_value

    return correct_answers


def extract_questions_answers_and_choices(html_content: bytes) -> dict:
    """
    從給定的 HTML 內容中提取每個問題的文本、答對的 entry ID、對應的答案值和所有選項。

    :param html_content: 包含 HTML 的位元組
    :return: 字典形式的 {
        entry_id: {
            'question': question_text,
            'answer': answer_value,
            'choices': [choices_list]
        }
    }
    """
    soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
    results = {}

    # 找到所有包含問題的區塊
    question_divs = soup.find_all('div', class_='Qr7Oae', role='listitem')

    for q_div in question_divs:
        # 初始化存儲數據的字典
        question_data = {
            'question': None,
            'answer': None,
            'choices': []
        }

        # --------------
        # 提取問題文字
        if not (heading_div := q_div.find('div', role='heading', attrs={'aria-level': '3'})):
            continue
            # print("警告: 無法找到問題的 heading div。")

        if not (question_span := heading_div.find('span', class_=re.compile(r'\bM7eMe\b'))):
            continue
            # print("警告: 無法找到具有 class 'M7eMe' 的 span 元素來提取問題文本。")

        if not (question_text := question_span.get_text(strip=True)):
            continue
            # print("警告: 問題文本的 span 標籤內沒有文字內容。")

        if question_text in ignored_questions: continue
        question_data['question'] = question_text

        # --------------
        # 提取所有選項
        for span in q_div.find_all('span', class_=re.compile(r'\bOIC90c\b')):
            if not (option_text := span.get_text(strip=True)):
                continue
                # print("警告: 某個選項的 span 標籤內沒有文字內容。")

            # 將選項的格式從 "A. equivalent" 改為 "A: equivalent"
            formatted_option = re.sub(r'^([A-Z])\.\s*', r'\1: ', option_text)
            question_data['choices'].append(formatted_option)

        # 嘗試找到此問題對應的 hidden input，該 input 包含 entry ID 和正確答案值

        if hidden_input := q_div.find('input', {'type': 'hidden', 'name': re.compile(r'^entry\.\d+$')}):
            entry_id = hidden_input.get('name')
            answer_value = hidden_input.get('value')

            if not entry_id or not answer_value:
                # print(f"警告: 找到的 hidden_input 缺少 name 或 value。")
                continue
            question_data['answer'] = answer_value
            results[entry_id] = question_data
            continue

        # 如果沒有 hidden input，嘗試從帶有 '答對' 標示的選項中提取答案
        # 查找包含 class 'IK9nwb' 的選項，這通常是正確的選項
        if not (correct_option_div := q_div.find('div', class_=re.compile(r'\bIK9nwb\b'))):
            # print("警告: 無法找到正確的選項，且沒有 hidden input。")
            continue

        if not (span_element := correct_option_div.find('span', class_=re.compile(r'\bOIC90c\b'))):
            # print("警告: 正確選項缺少 class 'OIC90c' 的 span 元素。")
            continue

        if not (answer_value := span_element.get_text(strip=True)):
            # print("警告: 正確選項的 span 標籤內沒有文字內容。")
            continue

        # 使用 data-item-id 作為 entry_id
        entry_id = q_div.get('data-item-id', f"auto_entry_{len(results) + 1}")
        question_data['answer'] = answer_value
        results[entry_id] = question_data

    return results
