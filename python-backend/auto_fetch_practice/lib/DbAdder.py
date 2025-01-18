import re
from dataclasses import dataclass
from typing import Dict, Any, List

import requests

from auto_fetch_practice.lib.FormExtractor import extract_questions_answers_and_choices


@dataclass
class Quiz:
    part: int
    topic: str
    form_url: str
    ans_url: str = ''

    def __hash__(self):
        return hash(self.ans_url)


def process_results(input_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    處理輸入的字典，根據以下規則處理 'question' 和 'answer' 字段：

    1. 問題 (question):
       - 移除所有換行符。
       - 將連續多個 \xa0 替換為一個半形空白。
       - 如果以 "\d\." 開頭，確保點後有且只有一個空格。

    2. 答案 (answer):
       - 如果以 "[A-Z]\." 開頭，確保點後有且只有一個空格。

    3. 選項 (choices):
       - 將選項中的 "." 替換為 ": "（例如 "A. equivalent" 轉換為 "A: equivalent"）。

    :param input_dict: 原始的字典，結構為 {entry_id: {"question": ..., "answer": ..., "choices": [...]}}
    :return: 處理後的字典，結構相同但內容已根據規則處理。
    """

    def process_question(text: str) -> str:
        # 移除所有換行符
        text = text.replace('\n', ' ')

        # 替換連續多個 \xa0 為一個半形空白
        text = re.sub(r'\xa0+', ' ', text)

        # 處理以 "\d\." 開頭的情況，確保點後有且只有一個空格
        text = re.sub(r'^(\d+)\.(?!\s)', r'\1. ', text)  # 如果點後沒有空格，補上一個空格
        text = re.sub(r'^(\d+)\.\s+', r'\1. ', text)  # 如果點後有多個空格，替換為一個空格
        text = re.sub(r"[\x00-\x1F\x7F]", '', text)

        return text.strip()

    def process_answer(text: str) -> str:
        # 處理以 "[A-Z]\." 開頭的情況，確保點後有且只有一個空格
        text = re.sub(r'^([A-Z])\.(?!\s)', r'\1. ', text)  # 如果點後沒有空格，補上一個空格
        text = re.sub(r'^([A-Z])\.\s+', r'\1. ', text)  # 如果點後有多個空格，替換為一個空格
        text = re.sub(r"[\x00-\x1F\x7F]", '', text)

        return text.strip()

    def process_choices(choices: List[str]) -> List[str]:
        processed = []
        for choice in choices:
            # 將選項中的 "." 替換為 ": "（例如 "A. equivalent" 轉換為 "A: equivalent"）
            choice = re.sub(r'^([A-Z])\.\s*', r'\1: ', choice)
            choice = re.sub(r"[\x00-\x1F\x7F]", '', choice)
            processed.append(choice)
        return processed

    processed_dict = {}

    for entry_id, data in input_dict.items():
        processed_data = {}

        # 處理 question
        raw_question = data.get("question", "")
        processed_question = process_question(raw_question)
        processed_data["question"] = processed_question

        # 處理 answer
        raw_answer = data.get("answer", "")
        processed_answer = process_answer(raw_answer)
        processed_data["answer"] = processed_answer

        # 處理 choices
        raw_choices = data.get("choices", [])
        processed_choices = process_choices(raw_choices)
        processed_data["choices"] = processed_choices

        # 添加到結果字典
        processed_dict[entry_id] = processed_data

    return processed_dict


def upsert(quiz: Quiz, api_endpoint: str, auth_token: str) -> None:
    """
    處理試題，提取問題與答案，並將結果發送至指定的 API 端點。

    :param quiz: 包含數據資料
    :param api_endpoint: API 的基礎 URL。
    :param auth_token: 用於授權的 Bearer Token。
    """

    try:
        if 'reurl' in quiz.ans_url:
            response = requests.get(quiz.ans_url, allow_redirects=True)
            final_url = response.url
            content = requests.get(final_url).content
        else:
            content = requests.get(quiz.ans_url).content
    except requests.RequestException as e:
        print(f"Error fetching URL {quiz.ans_url}: {e}")
        return

    try:
        questions_answers = extract_questions_answers_and_choices(content)
        dict_data = process_results(questions_answers)
    except Exception as e:
        print(f"Error processing data from {quiz.ans_url}: {e}")
        return

    # print(f"\n{quiz.part:02}: {quiz.topic: >10} -> {quiz.ans_url}")
    # for entry_id, data in dict_data.items():
    #     print(f'"{entry_id}": {{')
    #     print(f'    "question": "{data["question"]}",')
    #     print(f'    "answer": "{data["answer"]}",')
    #     print(f'    "choices": {data["choices"]}')
    #     print('},\n')

    try:
        req = requests.post(
            f"{api_endpoint}/api/add-practices",
            params={"part": quiz.part, "topic": quiz.topic.lower()},
            json=dict_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        req.raise_for_status()
        # print(f'{quiz.part:02}: {quiz.topic: >10} - {quiz.ans_url}: {req.text}')
    except requests.RequestException as e:
        # print(f"Error posting data to API for {quiz.ans_url}: {e}")
        raise e
