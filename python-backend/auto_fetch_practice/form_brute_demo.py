import logging
import time
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup

from lib.FormSubmitter import FormSubmitter

# 定義用戶數據
USERS = [
    # {
    #     "name": "張小明",
    #     "department": "四三十二",
    #     "student_id": "A12345678",
    #     "department_full": "建築系(所)",
    #     "email": "example@example.com",
    #     "phone": "0912345678",
    #     "motivation": "CC105B000"
    # },
]

# 主題映射
TOPICS_MAPPER = {
    '托福': 'toefl',
    '學術': 'academic',
    '微積分': 'calculus',
    '雅思': 'ielts',
    '電機': 'pvqc-ee',
    '電子': 'pvqc-ee',
    '商業': 'pvqc-bm',
    '機械': 'pvqc-me',
    '多媒體': 'pvqc-dmd',
    '計算機': 'pvqc-ict',
}

# 部分映射
PART_MAPPER = {
    '二十': 20,
    '十九': 19,
    '十八': 18,
    '十七': 17,
    '十六': 16,
    '十五': 15,
    '十四': 14,
    '十三': 13,
    '十二': 12,
    '十一': 11,
    '十': 10,
    '九': 9,
    '八': 8,
    '七': 7,
    '六': 6,
    '五': 5,
    '四': 4,
    '三': 3,
    '二': 2,
    '一': 1,
}


class UserData:
    """用戶資料類，用於儲存表單自動填寫所需的用戶信息"""

    def __init__(self, data: Dict):
        """
        初始化用戶數據 (簡化版)

        Args:
            data: 包含用戶資料的字典
        """
        self.name = data.get("name", "")
        self.department = data.get("department", "")
        self.student_id = data.get("student_id", "")
        self.department_full = data.get("department_full", "")
        self.email = data.get("email", "")
        self.phone = data.get("phone", "")
        self.motivation = data.get("motivation", "")

    def get_indicate_mapper(self) -> Dict[Tuple[str, ...], str]:
        """
        返回用於表單自動填寫的映射字典

        Returns:
            映射字典，鍵為可能的欄位名稱元組，值為對應的用戶資料
        """
        return {
            ("姓名", "名字", "名字 / Name", "name"): self.name,
            ("科系", "科系 / Department"): self.department,
            ("學號", "學號 / Student ID", "student id"): self.student_id,
            ("系所", "系所／單位", "系所／單位 Department"): self.department_full,
            ("E-mail", "Email", "電子郵件", "電子郵件 / E-mail"): self.email,
            ("手機", "手機號碼", "電話", "phone"): self.phone,
            ("測驗動機", "測驗動機 (修讀整合式英語課程之同學請務必填寫正確)"): self.motivation,
        }


def extract_content_title_and_url(html_content: bytes) -> List[Dict[str, str]]:
    """從 HTML 中提取標題、URL"""
    soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')

    # 提取所有具有 class 'mtitle' 的 div 中的 a 標籤
    mtitle_divs = soup.find_all('div', class_='mtitle')

    extracted_data = []
    for mtitle in mtitle_divs:
        try:
            if a_tag := mtitle.find('a'):
                title = a_tag.get_text(strip=True)
                url = a_tag.get('href')
                extracted_data.append({'title': title, 'url': url})
                print(f"提取到標題和 URL: 標題={title}, URL={url}")
        except Exception as e:
            print(f"提取標題和 URL 時發生錯誤: {e}")

    print(f"共提取到 {len(extracted_data)} 條標題和 URL。")
    return extracted_data


def extract_content_form_url(html_content: bytes) -> List[Dict[str, str]]:
    """
    從 HTML 中提取 Google Form 的 URL、Topic、Part

    Args:
        html_content (bytes): HTML 內容

    Returns:
        List[Dict[str, str]]: 包含提取結果的列表
    """
    soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
    forms = []

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if not href.startswith('https://forms.gle/') and 'docs.google.com/forms' not in href:
            continue

        try:
            if previous_text := list(a_tag.previous_siblings)[0]:
                topic_raw = previous_text.strip()
            else:
                topic_raw = ''

            topic = None
            part = None

            # Extract "topic" from leading text
            for key, value in TOPICS_MAPPER.items():
                if key in topic_raw:
                    topic = value
                    break

            # Extract "topic" from page title
            if topic is None and soup.title:
                for key, value in TOPICS_MAPPER.items():
                    if key in soup.title.text:
                        topic = value
                        break

            # Extract "part" from page title
            if soup.title:
                for key, value in PART_MAPPER.items():
                    if key in soup.title.text:
                        part = value
                        break

            form_title = a_tag.get_text(strip=True) or "未命名表單"

            form_data = {
                'title': form_title,
                'url': href,
                'topic': topic,
                'part': part
            }

            forms.append(form_data)
            print(f"提取到 Google Form: {form_data}")

        except Exception as e:
            print(f"處理 Google Form URL 時出錯: {e}")

    return forms


def get_answers_from_api(part: int, topic: str) -> Dict[str, str]:
    """
    從 API 獲取答案

    Args:
        part: 部分編號
        topic: 主題名稱

    Returns:
        entry_id 到答案的映射字典
    """
    try:
        api_url = f"https://ntust-eng-backend.xinshou.tw/api/v1/practice/{part}/{topic}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()
        entries = data.get("entries", [])

        # 建立 entry_id 到答案的映射
        answers = {}
        for entry in entries:
            entry_id = entry.get("entry_id")
            answer = entry.get("answer")
            if entry_id and answer:
                answers[entry_id] = answer

        return answers

    except Exception as e:
        logging.error(f"從 API 獲取答案時出錯: {e}")
        print(f"從 API 獲取答案時出錯: {e}")
        return {}


def process_google_form(form_data: Dict[str, str], users: List[UserData]) -> None:
    """
    處理單個 Google Form：設置答案並為每個用戶自動提交

    Args:
        form_data: 表單數據，包含 url, topic, part
        users: 用戶數據列表
    """
    form_url = form_data['url']
    topic = form_data.get('topic')
    part = form_data.get('part')
    title = form_data.get('title', '未命名表單')

    print(f"\n處理表單: {title}")
    print(f"URL: {form_url}")
    if topic and part:
        print(f"主題: {topic}, 部分: {part}")
    print("=" * 60)

    try:
        # 初始化表單提交器
        form_submitter = FormSubmitter(url=form_url, ignore_out_bounded=True)

        # 如果提供了部分和主題，從 API 獲取答案
        if part is not None and topic is not None:
            print(f"從 API 獲取答案 (part={part}, topic={topic})...")
            answers = get_answers_from_api(part, topic)
            if answers:
                print(f"成功獲取到 {len(answers)} 個答案")
                form_submitter.guess()
                # form_submitter.set_answer(answers)
            else:
                raise ValueError("獲取答案失敗，使用預設答案")
                print("未能從 API 獲取答案，使用預設答案")
                default_answers = {
                    'entry.1000665440': 'labeled',
                    # ... 其他預設答案
                }
                form_submitter.set_answer(default_answers)
        else:
            raise ValueError("未提供部分或主題")
            # 如果沒有提供部分和主題，使用預設答案
            print("無法識別主題和部分，使用預設答案...")
            default_answers = {
                'entry.1000665440': 'labeled',
                # ... 其他預設答案
            }
            form_submitter.set_answer(default_answers)

        # 打印答案
        print("\n表單答案:")
        form_submitter.print_answer_dict()

        # 為每個用戶提交表單
        for i, user in enumerate(users):
            print(f"\n[用戶 {i + 1}/{len(users)}] 提交表單: {user.name} ({user.student_id})")

            # 自動提交表單
            result = form_submitter.auto_submit(
                indicate_mapper=user.get_indicate_mapper(),
                keyword_mapper={}  # 可以根據需要擴展關鍵詞映射
            )

            # 打印結果
            # if result:
            #     print(f"提交成功: {user.name}")
            # else:
            #     print(f"提交失敗: {user.name}")

            # 等待一段時間，避免頻繁請求
            time.sleep(2)

    except Exception as e:
        logging.error(f"處理表單時出錯: {form_url} - {e}")
        print(f"處理表單時出錯: {e}")


def main():
    """
    主函數：按照 app.py 中的 check_for_updates 邏輯獲取表單並處理
    """
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='form_brute.log'
    )

    # 創建用戶數據列表
    users = [UserData(user_data) for user_data in USERS]

    # 定義目標 URL
    TARGET_URL = "https://lc.ntust.edu.tw/p/403-1070-1828-1.php?Lang=zh-tw"

    try:
        # 第一步：從目標 URL 獲取所有文章連結
        print(f"從 {TARGET_URL} 獲取連結...")
        response = requests.get(TARGET_URL, timeout=30)
        response.raise_for_status()

        content_links = extract_content_title_and_url(response.content)

        if not content_links:
            print("未找到任何連結，請檢查目標 URL 是否正確。")
            return

        print(f"\n找到 {len(content_links)} 個連結:")
        for i, link in enumerate(content_links):
            print(f"{i + 1}. {link['title']}")
            print(f"   URL: {link['url']}")

        # 讓用戶選擇要處理的連結
        while True:
            try:
                choice = input("\n請選擇要處理的連結編號 (例如: 1,3,5 或 'all' 處理所有, 'q' 退出): ")

                if choice.lower() == 'q':
                    print("程序已退出。")
                    return

                if choice.lower() == 'all':
                    selected_indices = range(len(content_links))
                    break

                # 解析用戶的選擇
                selected_indices = []
                for part in choice.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        selected_indices.extend(range(start - 1, end))
                    elif part:
                        selected_indices.append(int(part) - 1)

                # 驗證選擇的索引
                if any(idx < 0 or idx >= len(content_links) for idx in selected_indices):
                    print(f"無效的選擇。請輸入 1 到 {len(content_links)} 之間的數字。")
                    continue

                if not selected_indices:
                    print("未選擇任何連結。")
                    continue

                break

            except ValueError:
                print("無效的輸入格式。請輸入數字，例如: 1,3,5")
                continue

        # 第二步：處理選擇的連結，從中提取 Google Form
        all_forms = []
        for idx in selected_indices:
            content_link = content_links[idx]
            print(f"\n訪問連結 {idx + 1}/{len(selected_indices)}: {content_link['title']}")

            try:
                req = requests.get(content_link['url'], timeout=30)
                if req.status_code != 200:
                    print(f"無法訪問 URL: {content_link['url']}, 狀態碼: {req.status_code}")
                    continue

                # 提取 Google Form
                forms = extract_content_form_url(req.content)

                if not forms:
                    print("未在此連結中找到 Google Form。")
                    continue

                all_forms.extend(forms)
                print(f"在此連結中找到 {len(forms)} 個 Google Form。")

            except Exception as e:
                print(f"處理連結時出錯: {e}")

        # 顯示找到的所有表單
        if not all_forms:
            print("\n未找到任何 Google Form，請檢查連結是否包含表單。")
            return

        print(f"\n共找到 {len(all_forms)} 個 Google Form:")
        for i, form in enumerate(all_forms):
            topic_str = f", 主題: {form['topic']}" if form['topic'] else ""
            part_str = f", 部分: {form['part']}" if form['part'] is not None else ""
            print(f"{i + 1}. {form['title']}{topic_str}{part_str}")
            print(f"   URL: {form['url']}")

        # 讓用戶選擇要處理的表單
        while True:
            try:
                choice = input("\n請選擇要處理的表單編號 (例如: 1,3,5 或 'all' 處理所有, 'q' 退出): ")

                if choice.lower() == 'q':
                    print("程序已退出。")
                    return

                if choice.lower() == 'all':
                    selected_form_indices = range(len(all_forms))
                    break

                # 解析用戶的選擇
                selected_form_indices = []
                for part in choice.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        selected_form_indices.extend(range(start - 1, end))
                    elif part:
                        selected_form_indices.append(int(part) - 1)

                # 驗證選擇的索引
                if any(idx < 0 or idx >= len(all_forms) for idx in selected_form_indices):
                    print(f"無效的選擇。請輸入 1 到 {len(all_forms)} 之間的數字。")
                    continue

                if not selected_form_indices:
                    print("未選擇任何表單。")
                    continue

                break

            except ValueError:
                print("無效的輸入格式。請輸入數字，例如: 1,3,5")
                continue

        # 處理選擇的表單
        for idx in selected_form_indices:
            form = all_forms[idx]
            print(f"\n處理表單 {idx + 1}/{len(selected_form_indices)}: {form['title']}")
            process_google_form(form, users)

        print("\n所有選擇的表單處理完成！")

    except Exception as e:
        logging.error(f"程序執行時發生錯誤: {e}")
        print(f"程序執行時發生錯誤: {e}")


if __name__ == '__main__':
    main()
