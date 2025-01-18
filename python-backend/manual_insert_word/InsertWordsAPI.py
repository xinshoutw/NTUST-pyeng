import json
import os
import sys
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

API_ENDPOINT = os.getenv('API_ENDPOINT')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}


def extract_part_number(part_dir: str):
    """
    從資料夾名稱中提取 part number。
    """
    part_name = os.path.basename(os.path.normpath(part_dir))
    try:
        part_number = int(part_name)
        return part_number
    except ValueError:
        print(f"Unknown int number of directory: '{part_dir}'")
        return None


def insert_words(part: int, topic: str, words_data_list: list):
    """
    一次插入多個單字，統一用一筆 API 請求發送。
    words_data_list: [
        {
            "word": "...",
            "pos": "...",
            "meaning": "...",
            "pronunciations": [...],
            "definitions": [...],
            "verbs": [...]
        },
        ...
    ]
    """
    payload = {
        "words": []
    }

    # 統一將共用的 part / topic 與各單字的內容組合到 payload
    for wd in words_data_list:
        payload["words"].append({
            "part": part,
            "topic": topic,
            "word": wd['word'],
            "pos": wd.get('pos', ''),
            "meaning": wd.get('meaning', ''),
            "pronunciations": wd.get('pronunciations', []),
            "definitions": wd.get('definitions', []),
            "verbs": wd.get('verbs', [])
        })

    try:
        response = requests.post(f'{API_ENDPOINT}/add-words', headers=HEADERS, json=payload)
        if response.status_code in [200, 201]:
            print(f"Inserted {len(words_data_list)} words into part {part}, topic '{topic}' via API.")
        elif response.status_code == 409:
            # 409 通常表示衝突（重複資料），但也可能是部分成功、部分衝突
            print(f"Some or all words already exist under part {part} and topic '{topic}'. Skipping insertion.")
        else:
            print(f"Error inserting words (HTTP {response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Exception raised during insertion for {len(words_data_list)} words: {e}")


def fetch_word_data(word):
    """
    從 dictionary-api.eliaschen.dev 抓取單字資訊。
    """
    api_url = f"https://dictionary-api.eliaschen.dev/api/dictionary/en-tw/{quote(word)}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            word_data = {
                'pronunciations': data.get('pronunciation', []),
                'definitions': data.get('definition', []),
                'verbs': data.get('verbs', [])
            }
            return word_data
        elif response.status_code in [404, 504]:
            # 單字未找到或超時，返回空結構以保留字段結構
            return {
                'pronunciations': [],
                'definitions': [],
                'verbs': []
            }
        else:
            print(f"Error fetching word '{word}': HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request exception for word '{word}': {e}")
        return None


def process_words_list(part: int, topic: str, words_list: list):
    """
    先逐筆抓取 dictionary 資料並整合，最後一次性呼叫 insert_words 。
    """
    processed_words = []  # 用來暫存所有處理過後的單字資料

    for item in tqdm(words_list):
        word = item.get('word')
        pos = item.get('pos', '')
        meaning = item.get('meaning', '')

        if not word:
            print(f"Missing 'word' field in item: {item}. Skipping.")
            continue

        # 從 dictionary-api 取得額外欄位
        word_data = fetch_word_data(word)
        if word_data is None: continue

        # 把原有 JSON 中的 pos / meaning 覆蓋回 dictionary-api 回傳的結構
        word_data['word'] = word
        word_data['pos'] = pos or word_data.get('pos', '-')
        word_data['meaning'] = meaning or word_data.get('meaning', '')

        processed_words.append(word_data)

    # 全部整合完之後，再一次性插入到遠端資料庫
    if processed_words:
        insert_words(part, topic, processed_words)
    else:
        print(f"No valid words to insert for Part {part}, Topic '{topic}'.")


def process_json_file(part: int, topic: str, file_path: str):
    """
    打開指定檔案並讀取 JSON，然後調用 process_words_list。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        words_list = json.load(f)

    process_words_list(part, topic, words_list)


def process_json_stdin(part: int, topic: str):
    """
    從 stdin 讀入 JSON 字串，並用相同流程新增單字。
    用法範例：cat somefile.json | python myscript.py
    """
    words_list = json.load(sys.stdin)
    # words_list 應該是一個列表: [ { "word": "...", "pos": "...", "meaning": "..."}, ... ]
    process_words_list(part, topic, words_list)


def process_json_files(part_number: int, part_dir: str):
    """
    處理指定 part 目錄下的所有 .json 檔案。
    """
    for file_name in os.listdir(part_dir):
        if not file_name.endswith('.json'):
            continue

        topic_name = os.path.splitext(file_name)[0]
        file_path = os.path.join(part_dir, file_name)

        print(f"Processing Part {part_number}, Topic '{topic_name}'")
        process_json_file(part_number, topic_name, file_path)


def process_part_directory(part_dir: str):
    """
    以資料夾為單位，找出該資料夾內的所有 .json 檔並處理：
    - 目錄名稱會被視作 part number
    - 檔名(不含副檔名) 會被視作 topic
    """
    if not os.path.isdir(part_dir):
        print(f"Unknown file of '{part_dir}', must be a directory")
        return

    part_number = extract_part_number(part_dir)
    if part_number is None:
        return

    process_json_files(part_number, part_dir)


def process_traversed_directory(root_dir: str):
    """
    遞迴處理多個 part 目錄，對每個 part 目錄下的 .json 檔執行新增流程。
    """
    for part_name in tqdm(os.listdir(root_dir), desc="Processing parts"):
        part_path = os.path.join(root_dir, part_name)
        if not os.path.isdir(part_path):
            continue

        part_number = extract_part_number(part_path)
        if part_number is None:
            print(f"Skipping directory '{part_name}' as it is not a valid part number.")
            continue

        process_part_directory(part_path)


def main():
    ...
    # process_traversed_directory('./training')
    # process_part_directory('./training/7')
    # process_json_stdin(part=6, topic="stdinTopic")
    # process_part_directory('./training/11')

    # PVQC 電機電子: pvqc-ee


#     process_words_list(5, 'pvqc-ee', json.loads("""
#     [
#   {
#     "word": "anthropologist",
#     "pos": "n",
#     "meaning": "人類學家"
#   },
#   {
#     "word": "mound",
#     "pos": "n",
#     "meaning": "塚；土石堆、小丘"
#   }
# ]
#     """.strip()))


if __name__ == '__main__':
    main()
