# auto_fetch_practice

這是一個全自動化爬蟲與表單提交系統，負責從語言中心等來源定期抓取最新單字資訊、作答取得正確答案，並將結果透過後端 API 寫入資料庫。

---

## 功能說明

1. 定期檢查目標網址：從語言中心網站抓取最新單字表清單。
2. 自動提取作答表單：取得作答網站的 Google Form 連結。
3. 隨機爆破作答：利用程式隨機填寫選項，並自動找出正確答案。
4. 答案紀錄：將正確答案上傳至後端 API，更新資料庫內容。

---

## 檔案結構

```bash
auto_fetch_practice/
├── app.py               # 主程式，排程與定期檢查
├── form_brute_demo.py   # FormSubmitter 範例程式
├── lib
│   ├── DbAdder.py       # 與API互動的橋樑，包含Quiz資料結構與上傳流程
│   ├── FormExtractor.py # Google Form資料解析與答案提取
│   └── FormSubmitter.py # 與Google Form互動的主要類別，提供自動爆破與結果取得
├── processed_urls.json  # 已處理過的表單/網址紀錄
├── start.sh             # (可選) 啟動或排程腳本
└── web_demo
    ├── app.py           # 測試/示範用後端
    ├── public/          # 靜態檔案或表單範例
    └── start.sh         # (可選) 測試啟動腳本
```

檔案重點

- `app.py`
    - 整個自動化流程的核心入口。
    - 使用 `BlockingScheduler` (APScheduler) 排程定期檢查目標網站，若有新表單網址則觸發處理流程：
    - 解析表單 URL
    - 隨機作答並取得正確答案
    - 透過 API (DbAdder) 上傳結果
    - 具備載入與保存 `processed_urls.json` 來避免重複處理。
- `form_brute_demo.py`
    - `FormSubmitter` 類別使用的範例示範。
    - 顯示如何引入 `FormSubmitter`，並以爆破方式填寫 Google Form 並以特定身分提交。
- `lib/`
    - `DbAdder.py`
        - 負責與後端 API 溝通、上傳練習結果。
        - 主要類別 `Quiz` 用於儲存 part, topic, form_url 等資訊。
        - 函式：
            - `process_results`：清理問題與答案字串
            - `upsert`：透過 API 寫入或更新資料庫
    - `FormExtractor.py`
        - Google Form 的解析邏輯：
        - 取得表單的加載資料 `FB_PUBLIC_LOAD_DATA_`
        - 解析出每個問題、選項、正確答案與對應的 entry ID
        - 提供一系列函式如 `extract_questions_answers_and_choices`，可將 HTML 分析並轉為結構化的題目/答案/選項資料。
    - `FormSubmitter.py`
        - 負責與 Google Form 互動：
            - 讀取表單結構
            - 自動爆破 (guess) 或手動指定答案
            - 送出表單請求並抓取回饋頁面的正確答案
        - 提供便利方法，如 `auto_submit`、`get_ans_url` 等，可整合自動化流程。
- `processed_urls.json`
    - 已處理成功的 URL 紀錄檔，避免重複提交。
- `web_demo/`
    - 供測試或示範用的小型後端範例，如：模擬真正的作答網站，或顯示表單提交效果。
- `start.sh`
    - 可能用於一鍵啟動排程執行的腳本。

---

## 使用方式

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 設定環境變數

`API_ENDPOINT`：後端 API 的 URL
`AUTH_TOKEN`：後端授權使用的 Token
`TARGET_URL`：語言中心或其他來源網站的目標首頁
`STATE_FILE`：紀錄已處理網址的檔案路徑 (默認 `processed_urls.json`)

### 執行主程式

`./start.sh` 或直接執行。

- 如使用 APScheduler，將自動依排程檢查新表單，並執行爆破作答、上傳結果。
    ```bash
    python app.py
    ```

### 測試/示範

`form_brute_demo.py`：展示 `FormSubmitter` 互動示例。
`web_demo/` 下的 `app.py`：可啟動模擬網站 `start.sh` 進行本地演示。

---

## 開發筆記

- lib 資料夾：集中爬蟲與表單邏輯，維持良好結構化。
- DbAdder：處理題目解析後與外部 API 溝通。使用 dataclass Quiz 做基礎資訊封裝。
- `FormExtractor` 專職 HTML / JSON 解析。
- `FormSubmitter` 負責送出表單、爆破猜測，或手動指定答案。
- 排程：`scheduler` 具備 `scheduled_job` 與 `check_for_updates`，可根據需求設置執行頻率。

## 注意事項

- 本程式依賴對目標表單的解析與猜測邏輯，若目標表單結構大幅變動，需要同步更新解析方法。
- 本專案僅用於學習用途，請勿從事惡意或不被允許的行為。
- `processed_urls.json` 需妥善維護，避免多次處理同一表單產生重複資料。

---

## 授權與貢獻

- 本專案採用 Apache 授權
- 歡迎提交 Issues、Pull Requests 改進此自動爬蟲流程！
