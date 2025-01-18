import random
import time
from copy import deepcopy

from .FormExtractor import *

# 選項超過 15 個會要求使用者手動選擇
MANUAL_CHECK_SIZE = 15


class FormSubmitter:
    def __init__(self, url: str, ignore_out_bounded=False):
        self._url: str  # 目標表單網址
        self._ignore_out_bounded = ignore_out_bounded  # 忽略過多選項
        self._max_guess_count = 1  # 最大選項個數
        self._question_mapper = {}  # 將 entry.id 映射到題目敘述
        self._request_sample = {}  # 原始題目
        self._request_final = {}  # 最終提交內容
        self._request_final_url = ""  # 最終提交結果 url
        self._require_entry_id: list[str] = []  # 填充題 id
        self._randomOffset: list[int] = []  # 隨機猜題偏移量
        self.__guess = False  # 是否已經有答案

        # 轉換為 response url
        self._url = get_form_response_url(url)
        self._request_sample = get_form_submit_request(self._url)

        for (entry_id, entry_dict) in self._request_sample.items():
            # 建立 mapper 映射原始題目
            self._question_mapper[entry_id] = entry_dict['question'].strip()

            # 處理多頁表單
            if entry_id == "pageHistory":
                self._request_final[entry_id] = entry_dict['value']
                continue

            # 選擇題
            if entry_dict["option_type"] in (FormType.MULTIPLE_CHOICE, FormType.DROPDOWN):
                options: list = entry_dict['options']
                options_size = len(options)
                # 找到最大選項數值
                if options_size <= MANUAL_CHECK_SIZE:
                    self._max_guess_count = max(self._max_guess_count, options_size)
                    continue

                if ignore_out_bounded:
                    self._request_final[entry_id] = options[random.randrange(options_size)]
                    continue

                # 處理過多選項的題目
                print("\n".join(f"{index:2}: {option}" for index, option in enumerate(options)))
                choose_input = input('Choose option index or keyword: ') or "0"
                if choose_input.isdecimal():
                    self._request_final[entry_id] = options[int(choose_input)]
                else:
                    # 找到符合關鍵字的第一個值
                    self._request_final[entry_id] = \
                        next((option for option in options if choose_input in option), options[0])

            # 填充題
            self._require_entry_id.append(entry_id)
            self._request_final[entry_id] = ' '  # 填一個空白

        self._randomOffset = [
            random.randrange(0, self._max_guess_count) for _ in range(len(self._request_sample))
        ]

    # 手動指定答案(dict)
    def set_answer(self, final: dict[str, str]):
        self._request_final = final
        self.__guess = True

    # 手動指定答案網站(str)
    def set_answer_url(self, result_url: str):
        answers = extract_correct_answers(requests.get(result_url).content, self._question_mapper)
        for (question, answer) in answers.items():
            self._request_final[question] = answer

        self._request_final_url = result_url
        self.__guess = True

    # 印出答案(字串)
    def print_answer(self):
        if not self.__guess: self.guess()
        for (key, ans) in self._request_final.items():
            print(f'{(self._question_mapper[key]).strip()}\n {ans}\n')

    # 印出答案(dict)
    def print_answer_dict(self):
        if not self.__guess: self.guess()
        print(f"\nDict: {self._request_final.__repr__()}\n")

    # 印出答案網址
    def print_answer_web(self):
        if not self.__guess: self.guess()
        print(f"\nFinal ans: {self._request_final_url}\n")

    # 取得答案網址
    def get_ans_url(self) -> str:
        if not self.__guess: self.guess()
        return self._request_final_url

    # 自動提交表單
    def auto_submit(self, indicate_mapper: dict[tuple[str], str], keyword_mapper: dict[tuple[str], str]):
        if indicate_mapper is None: indicate_mapper = {}
        if keyword_mapper is None: keyword_mapper = {}

        if not self.__guess: self.guess()

        request_data = deepcopy(self._request_sample)
        request_data.update(self._request_final)

        # {('A', 'B'): 'C'}
        # change to
        # {'a': 'C', 'b': 'C'}
        indicate_lookup_table = {
            key.lower(): value for key_set, value in indicate_mapper.items() for key in key_set
        }
        keyword_lookup_table = {
            key.lower(): value for key_set, value in keyword_mapper.items() for key in key_set
        }

        for key, value in request_data.items():
            if value != " ":
                continue

            inp = ""
            for mapK, mapV in indicate_lookup_table.items():
                if mapK == self._question_mapper[key].lower():
                    inp = mapV
                    break

            if inp == "":
                for mapK, mapV in keyword_lookup_table.items():
                    if mapK in self._question_mapper[key].lower():
                        inp = mapV
                        break

            if inp == "":
                inp = input(f'請輸入 "{self._question_mapper[key]}": ')
            request_data[key] = inp

        print(request_data)
        input("\n檢查請求是否正確!! [ENTER]")

        res = requests.post(self._url, data=request_data, timeout=10)
        res.raise_for_status()
        result_url = BeautifulSoup(res.content, 'html.parser', from_encoding='utf-8') \
            .find('a', attrs={'aria-label': '查看分數'})['href']
        print(f"查看分數: {result_url}")

    # 爆破
    def guess(self):
        # with (tqdm(total=self._max_guess_count) as tq):
        #     cnt = 0
        #     while cnt <= self._max_guess_count and \
        #             len(self._request_final) != len(self._request_sample):
        #         self._guess(cnt)
        #         cnt += 1
        #         tq.update(1)
        #         tq.refresh()
        #     tq.update(self._max_guess_count - cnt)
        #     tq.refresh()
        #     tq.close()
        for cnt in range(self._max_guess_count):
            self._guess(cnt)
            if len(self._request_final) == len(self._request_sample):
                break
            time.sleep(1)

        self.__guess = True

    # 根據選項爆破
    def _guess(self, select_index: int):
        request_cur = {}

        for index, (entry_id, root_dict) in enumerate(self._request_sample.items()):
            # 已經知道答案
            if entry_id in self._request_final.keys():
                request_cur[entry_id] = self._request_final[entry_id]
                continue

            # 選擇題
            if root_dict['option_type'] in (FormType.MULTIPLE_CHOICE, FormType.DROPDOWN):
                options = root_dict["options"]
                optionCount = len(options)
                select_index_offset = (select_index + self._randomOffset[index]) % optionCount
                request_cur[entry_id] = options[select_index_offset]
                continue

            # 填充題
            if root_dict['option_type'] in (FormType.SHORT_ANSWER,):
                request_cur[entry_id] = " "
                continue

            raise Exception(f"Wrong value: {root_dict})")

        # 提交並解析結果
        res = requests.post(self._url, data=request_cur, timeout=10)
        res.raise_for_status()

        result_url = BeautifulSoup(res.content, 'html.parser', from_encoding='utf-8') \
            .find('a', attrs={'aria-label': '查看分數'})['href']

        answers = extract_correct_answers(requests.get(result_url).content, self._question_mapper)
        for (question, answer) in answers.items():
            self._request_final[question] = answer

        self._request_final_url = result_url
