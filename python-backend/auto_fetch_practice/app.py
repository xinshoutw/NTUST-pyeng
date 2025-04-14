import argparse
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Set, List, Dict
from zoneinfo import ZoneInfo

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from lib import DbAdder
from lib.DbAdder import Quiz
from lib.FormSubmitter import FormSubmitter

# 新增命令列參數處理
parser = argparse.ArgumentParser(description="自動獲取練習題的排程任務")
parser.add_argument('--env', type=str, default='.env', help='環境變數設定檔路徑')
parser.add_argument('--log-file', type=str, default='crawler.log', help='日誌檔案路徑')
parser.add_argument('--debug', action='store_true', help='啟用偵錯模式')
args = parser.parse_args()

# 設置日誌
log_dir = os.path.dirname(args.log_file)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format='%(asctime)s - %(levelname)-5s [%(name)s] -> %(message)s',
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(args.log_file, maxBytes=10 ** 6, backupCount=5)
    ]
)

logger = logging.getLogger("quiz-crawler")

# 載入環境變數
load_dotenv(args.env)

API_ENDPOINT = os.getenv('API_ENDPOINT')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TARGET_URL = os.getenv('TARGET_URL')
STATE_FILE = os.getenv('STATE_FILE')
CRON_EXPRESSION = os.getenv('CRON_EXPRESSION', '0 0 * * 1')  # 預設每週一凌晨執行

# 檢查環境變數
if not all([API_ENDPOINT, AUTH_TOKEN, TARGET_URL, STATE_FILE]):
    logger.error("環境變數設定不完整，請檢查 .env 檔案")
    logger.error(f"API_ENDPOINT: {API_ENDPOINT}")
    logger.error(f"AUTH_TOKEN: {'已設置' if AUTH_TOKEN else '未設置'}")
    logger.error(f"TARGET_URL: {TARGET_URL}")
    logger.error(f"STATE_FILE: {STATE_FILE}")
    exit(1)

# 確保狀態檔案目錄存在
state_dir = os.path.dirname(STATE_FILE)
if state_dir and not os.path.exists(state_dir):
    os.makedirs(state_dir)
    logger.info(f"已創建狀態檔案目錄: {state_dir}")

logger.info(f"爬蟲服務已啟動")
logger.info(f"API 端點: {API_ENDPOINT}")
logger.info(f"目標網址: {TARGET_URL}")
logger.info(f"狀態檔案: {STATE_FILE}")
logger.info(f"排程設定: {CRON_EXPRESSION}")

topics_mapper: Dict[str, str] = {
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

part_mapper: Dict[str, int] = {
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


def load_processed_urls() -> Set[str]:
    """載入已處理的 URL 列表"""
    if not os.path.exists(STATE_FILE):
        logger.info(f"狀態檔案 {STATE_FILE} 不存在，進行初始化。")
        return set()
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            logger.info(f"載入已處理的 URL，共 {len(data)} 條。")
            return set(data)
        except json.JSONDecodeError:
            logger.error(f"狀態檔案 {STATE_FILE} 無法解析為 JSON，初始化為空集合。")
            return set()


def save_processed_urls(urls: Set[str]) -> None:
    """保存已處理的 URL 列表"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(urls), f, ensure_ascii=False, indent=4)
    logger.info(f"已保存 {len(urls)} 條已處理的 URL 到 {STATE_FILE}。")


def extract_content_form_url(html_content: bytes) -> Set[Quiz]:
    """
    從 HTML 中提取 Google Form 的 URL、Topic、Part，返回 Quiz 資料類型

    Args:
        html_content (bytes): HTML 內容。

    Returns:
        Set[Quiz]: 包含提取結果的集合。
    """
    soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
    quiz_set = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if not href.startswith('https://forms.gle/'):
            continue

        try:
            if previous_text := list(a_tag.previous_siblings)[0]:
                topic_raw = previous_text.strip()
            else:
                topic_raw = ''

            topic: Optional[str] = None
            part: Optional[int] = None

            # Extract "topic" from leading text
            for key, value in topics_mapper.items():
                if key in topic_raw:
                    topic = value
                    break
            # Extract "topic" from page title
            if topic is None and soup.title:
                for key, value in topics_mapper.items():
                    if key in soup.title.text:
                        topic = value
                        break
            if topic is None:
                logger.warning(f'    - 未匹配到主題的 URL: {href}')
                continue

            # Extract "part" from page title
            if soup.title:
                for key, value in part_mapper.items():
                    if key in soup.title.text:
                        part = value
                        break
            if part is None:
                logger.warning(f'    - 未匹配到部分的 URL: {href}')
                continue

            quiz = Quiz(part=part, topic=topic, form_url=href)
            quiz_set.add(quiz)
            logger.info(f"    - 提取到新的 Quiz: {quiz}")
        except Exception as e:
            logger.error(f"    - 處理 URL 時發生錯誤 ({href}): {e}")

    return quiz_set


def process_google_form_url(quiz: Quiz) -> None:
    """
    處理單個 Google Form URL，並將結果上傳到 API。

    Args:
        quiz (Quiz): 包含表單資訊的 Quiz 物件。
    """
    try:
        submitter = FormSubmitter(quiz.form_url, True)
        submitter.guess()
        quiz.ans_url = submitter.get_ans_url()
        DbAdder.upsert(quiz, API_ENDPOINT, AUTH_TOKEN)
        logger.info(f"      成功處理並上傳 Quiz: {quiz}")
    except Exception as e:
        logger.error(f"      處理 Quiz 時發生錯誤 ({quiz.form_url}): {e}")


def extract_content_title_and_url(html_content: bytes) -> List[Dict[str, str]]:
    """從 HTML 中提取標題、URL 和 Google Form URL"""
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
                logger.debug(f"提取到標題和 URL: 標題={title}, URL={url}")
        except Exception as e:
            logger.error(f"提取標題和 URL 時發生錯誤: {e}")

    logger.info(f"共提取到 {len(extracted_data)} 條標題和 URL。")
    return extracted_data


def check_for_updates() -> None:
    """檢查目標網站是否有新的內容"""
    logger.info(f"開始檢查網站更新 ({TARGET_URL})...")

    try:
        response = requests.get(TARGET_URL, timeout=30)
        if response.status_code != 200:
            logger.error(f"無法訪問網站，狀態碼：{response.status_code}")
            return

        extracted_data = extract_content_title_and_url(response.content)
        processed_urls = load_processed_urls()
        new_items = []
        for item in extracted_data:
            url = item['url']
            if url not in processed_urls:
                new_items.append(item)
                processed_urls.add(url)

        if not new_items:
            logger.info("沒有新內容。")
            return

        logger.info(f"發現 {len(new_items)} 條新內容：")
        for item in new_items:
            logger.info(f"  - 標題：{item['title']} | URL：{item['url']}")

            try:
                req = requests.get(item['url'], timeout=30)
                if req.status_code != 200:
                    logger.error(f"    無法訪問 URL：{item['url']}，狀態碼：{req.status_code}")
                    continue

                if not (quiz_set := extract_content_form_url(req.content)):
                    logger.info("    未找到 Google Form 網址。")
                    continue

                for quiz in quiz_set:
                    logger.info(f"      處理 Quiz: {quiz}")
                    process_google_form_url(quiz)

            except requests.RequestException as e:
                logger.error(f"      訪問 URL 時發生錯誤 ({item['url']}): {e}")
            except Exception as e:
                logger.error(f"      處理項目時發生未知錯誤 ({item['url']}): {e}")

        # 保存更新後的已處理 URL
        save_processed_urls(processed_urls)

    except requests.RequestException as e:
        logger.error(f"檢查過程中發生網路錯誤：{e}")
    except Exception as e:
        logger.error(f"檢查過程中發生未知錯誤：{e}", exc_info=True)


def scheduled_job():
    """
    定義排程任務
    """
    logger.info("開始執行排程任務")
    try:
        check_for_updates()
        logger.info("排程任務執行完成")
    except Exception as e:
        logger.error(f"排程任務執行失敗：{e}", exc_info=True)


def main():
    """
    主函數，設定排程並啟動排程器。
    """
    scheduler = BlockingScheduler(timezone=ZoneInfo("Asia/Taipei"))  # UTC+8

    # 先執行一次檢查
    try:
        check_for_updates()
    except Exception as e:
        logger.error(f"初始檢查失敗：{e}", exc_info=True)

    # 設定排程觸發器
    if CRON_EXPRESSION == 'DEBUG':
        # 測試模式：每分鐘執行一次
        trigger = CronTrigger(minute='*/1')
        logger.warning("使用測試模式排程 (每分鐘執行一次)，不建議在生產環境使用")
    else:
        # 解析 cron 表達式
        try:
            minute, hour, day, month, day_of_week = CRON_EXPRESSION.split()
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
            )
            logger.info(f"使用排程: {CRON_EXPRESSION}")
        except Exception as e:
            logger.error(f"解析 CRON 表達式錯誤: {e}，使用預設排程 (每週一凌晨執行)")
            trigger = CronTrigger(day_of_week='mon', hour=0, minute=0)

    # 添加任務到排程器
    scheduler.add_job(
        scheduled_job,
        trigger=trigger,
        id='quiz_fetch_task',
        name='quiz_fetch_task',
        replace_existing=True,
    )

    logger.info("排程器已啟動")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("應用程式結束")
    except Exception as e:
        logger.error(f"排程器執行時發生錯誤：{e}", exc_info=True)


if __name__ == "__main__":
    main()
