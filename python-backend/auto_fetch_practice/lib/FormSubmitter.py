import random
import time
from copy import deepcopy
import logging
import functools

from .FormExtractor import *

logger = logging.getLogger(__name__)

def log_exceptions(default=None, reraise=False):
    """Decorator to log exceptions for methods.
    If reraise is True, exception is re-raised after logging; otherwise default is returned.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Error in {func.__qualname__}: {e}")
                if reraise:
                    raise
                return default
        return wrapper
    return decorator

# 選項超過 15 個會要求使用者手動選擇
MANUAL_CHECK_SIZE = 15


class FormSubmitter:
    @log_exceptions(reraise=True)
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
        self.__guessed = False  # 是否已經有答案

        # 轉換為 response url
        self._url = get_form_response_url(url)

        # 檢查網址使否有 "closedform" 關鍵字
        if 'closedform' in self._url:
            raise ValueError("The form is closed and cannot be submitted.")

        self._request_sample = get_form_submit_request(self._url)
        if not isinstance(self._request_sample, dict) or self._request_sample is None:
            logger.error(f"get_form_submit_request returned invalid data: {type(self._request_sample)}")
            raise ValueError("Invalid form submit request data; expected dict.")

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

                if self._ignore_out_bounded:
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
    @log_exceptions()
    def set_answer(self, final: dict[str, str]):
        self._request_final = final
        self.__guessed = True

    # 手動指定答案網站(str)
    @log_exceptions()
    def set_answer_url(self, result_url: str):
        if 'reurl' in result_url:
            response = requests.get(result_url, allow_redirects=True)
            result_url = response.url

        answers = extract_correct_answers(requests.get(result_url, allow_redirects=True).content, self._question_mapper)
        for (question, answer) in answers.items():
            if question in self._require_entry_id or question in self._request_final.keys():
                continue

            self._request_final[question] = answer

        # self._request_final_url = result_url
        self.__guessed = True

    # 印出答案(字串)
    @log_exceptions()
    def print_answer(self):
        if not self.__guessed: self.guess()
        for (key, ans) in self._request_final.items():
            print(f'{(self._question_mapper[key]).strip()}\n {ans}\n')

    # 印出答案(dict)
    @log_exceptions()
    def print_answer_dict(self):
        if not self.__guessed: self.guess()
        print(f"\nDict: {self._request_final.__repr__()}\n")

    # 印出答案網址
    @log_exceptions()
    def print_answer_web(self):
        print(f"\nFinal ans: {self.get_ans_url()}\n")

    @log_exceptions(reraise=True)
    def _parse_result_url(self, content) -> str:
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
        link = soup.find('a', attrs={'aria-label': '查看分數'})
        href = link['href'] if link and link.has_attr('href') else None
        if not href:
            raise ValueError('Result link not found in response HTML')
        return href

    # 取得答案網址
    @log_exceptions(default="")
    def get_ans_url(self) -> str:
        if not self.__guessed: self.guess()
        if not self._request_final_url:
            res = requests.post(self._url, data=self._request_final, timeout=10)
            res.raise_for_status()
            result_url = self._parse_result_url(res.content)
            self._request_final_url = result_url

        return self._request_final_url

    # 自動提交表單
    @log_exceptions()
    def auto_submit(
            self,
            indicate_mapper: dict[tuple[str, ...], str] = None,
            keyword_mapper: dict[tuple[str, ...], str] = None
    ):
        if indicate_mapper is None: indicate_mapper = {}
        if keyword_mapper is None: keyword_mapper = {}

        if not self.__guessed: self.guess()

        request_data = deepcopy(self._request_sample)
        request_data.update(self._request_final)

        # {('a', 'b'): 'C'}
        # change to
        # {'a': 'C', 'b': 'C'}
        indicate_lookup_table = {
            key.lower(): value for key_set, value in indicate_mapper.items() for key in key_set
        }
        keyword_lookup_table = {
            key.lower(): value for key_set, value in keyword_mapper.items() for key in key_set
        }

        for key, value in request_data.items():
            for mapK, mapV in indicate_lookup_table.items():
                if mapK == self._question_mapper[key].lower():
                    request_data[key] = mapV
                    break

        for key, value in request_data.items():
            if value != " ":
                continue

            for mapK, mapV in keyword_lookup_table.items():
                if mapK in self._question_mapper[key].lower():
                    request_data[key] = mapV
                    break

        for key, value in request_data.items():
            if value == " ":
                inp = input(f'請輸入 "{self._question_mapper[key]}": ')
                request_data[key] = inp

        print(request_data)
        # input("\n檢查請求是否正確!! [ENTER]")

        res = requests.post(self._url, data=request_data, timeout=10)
        res.raise_for_status()
        result_url = self._parse_result_url(res.content)
        print(f"查看分數: {result_url}")

    # 爆破
    @log_exceptions()
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

        if len(self._request_final) != len(self._request_sample):
            print("無法猜測所有答案，請手動輸入")
            self.print_answer_dict()
            exit(0)

            # cannot guess all answers
        self.__guessed = True

    # 根據選項爆破
    @log_exceptions()
    def _guess(self, select_index: int):
        request_cur = {}

        for index, (entry_id, root_dict) in enumerate(self._request_sample.items()):
            if "如何得知語言中心舉辦的活動訊息" in self._question_mapper[entry_id]:
                request_cur[entry_id] = "中心官網"
                continue

            # 已經知道答案
            if entry_id in self._request_final.keys():
                request_cur[entry_id] = self._request_final[entry_id]
                continue

            # 選擇題
            if root_dict['option_type'] in (FormType.MULTIPLE_CHOICE, FormType.DROPDOWN, FormType.CHECKBOXES):
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

        result_url = self._parse_result_url(res.content)

        answers = extract_correct_answers(requests.get(result_url).content, self._question_mapper)
        for (question, answer) in answers.items():
            self._request_final[question] = answer

        self._request_final_url = result_url
