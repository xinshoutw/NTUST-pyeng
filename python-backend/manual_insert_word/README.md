# manual_insert_word

此資料夾負責手動插入英文字詞至後端資料庫。主要包括以下功能：

- 透過本地的 JSON 檔案（或透過 stdin）讀入多個字詞資訊
- 依照 part / topic 分類
- 從字詞 API (`dictionary-api.eliaschen.dev`) 補充字詞的發音、定義、動詞變化等
- 一次性將整理後的字詞陣列，使用後端 API (`/add-words`) 插入資料庫

---

## 檔案結構

```bash
manual_insert_word/
├── InsertWordsAPI.py   # 主程式，提供讀取 JSON、抓取字典API補充，並插入後端API
├── README.md            # 你目前所閱讀的檔案
└── training/            # 預先分類好的 JSON 檔，每個資料夾名稱為 part number
    ├── 1
    │   ├── academic.json
    │   ├── calculus.json
    │   ├── ielts.json
    │   ├── pvqc-bm.json
    │   ├── pvqc-dmd.json
    │   ├── pvqc-ee.json
    │   ├── pvqc-ict.json
    │   ├── pvqc-me.json
    │   └── toefl.json
    ├── 9
    │   ├── academic.json
    │   ├── calculus.json
    │   ├── ielts.json
    │   └── toefl.json
    └── 10
        └── toefl.json
```

- `InsertWordsAPI.py`
    - main() 函式示範了幾種使用模式，包含：
        - 遞迴處理整個資料夾 (process_traversed_directory())
        - 處理單一 part 目錄 (process_part_directory())
        - 從 stdin 讀取 JSON 後插入 (process_json_stdin())
        - 直接在程式中以字串形式建立一份 JSON 後插入 (process_words_list())
    - 主要流程：
        - 從 JSON 讀取字詞清單
        - 可使用 fetch_word_data() 從外部 dictionary-api 抓取補充資料
        - 封裝 payload 後呼叫 insert_words() 一次性發送到後端 API
    - training/
        - 包含多個資料夾，每個資料夾代表一個 part 的編號 (e.g. 1, 9, 10...)
        - 內部每個 .json 檔名 (去掉副檔名) 對應一個 topic (如 calculus, toefl 等)
        - JSON 格式範例：
      ```json
      [
        {
          "word": "anthropologist",
          "pos": "n",
          "meaning": "人類學家"
        },
        {
          "word": "mound",
          "pos": "n",
          "meaning": "塚；土石堆、小丘"
        }
      ]
      ```
      其中每個物件可包含 word, pos, meaning，或更多欄位。

---

## InsertWordsAPI.py 主要流程

1. extract_part_number(part_dir)
    - 從資料夾路徑取得數字部分，視為 part 編號。
2. insert_words(part, topic, words_data_list)
    - 將指定 part、topic、以及多筆字詞資料做成 API 請求 payload，呼叫後端 `/add-words`。
3. fetch_word_data(word)
    - 從外部字典 API (`dictionary-api.eliaschen.dev`) 抓取發音、定義等，回傳給上層做合併。
4. process_words_list(part, topic, words_list)
    - 整合原始 JSON 字詞資料與 `fetch_word_data()` 之回傳資訊，最終一次 `insert_words()` 到後端。
5. process_json_file(part, topic, file_path)
    - 開啟並讀取 `.json` 檔，呼叫 `process_words_list()`。
6. process_json_stdin(part, topic)
    - 從標準輸入讀入 JSON 後，呼叫 `process_words_list()`。
7. process_json_files(part_number, part_dir)
    - 處理該 part_dir 下所有 `.json` 檔，每個檔名代表一個 topic。
8. process_part_directory(part_dir)
    - 以資料夾為單位：先取其 part number，再對裡面的 JSON 全部執行新增流程。
9. process_traversed_directory(root_dir)

依序進入多個 part 目錄（如 `1`, `2`, `3` ...），呼叫 `process_part_directory()`。

---

## 使用步驟

### 設定環境變數

- 在同層或上層路徑放置 `.env` 檔案，或自行於系統環境變數中設定。內容包含：
    ```bash
    API_ENDPOINT=https://your-backend-api
    AUTH_TOKEN=abc123
    ```

### 安裝套件

```bash
pip install -r requirements.txt
```

### 執行 InsertWordsAPI.py

- 直接透過 main() 內已經範例的幾行程式控制：
    ```bash
    python InsertWordsAPI.py
    ```
- 或自行在 main() 中修改 / 新增想要處理的目錄或檔案：
    ```bash
    # 示例：一次性處理 ./training 下的全部 part
    process_traversed_directory('./training')
    
    # 示例：只處理特定 part資料夾
    process_part_directory('./training/7')
    
    # 示例：從 stdin讀取
    cat somefile.json | python InsertWordsAPI.py
    ```

### 檢查輸出

- 成功插入會在 CLI 顯示 `Inserted X words into part N, topic 'xxx' via API.`
- 若已存在或衝突，可能會顯示 `Some or all words already exist under part ...`
- 若有錯誤 (e.g. 連線失敗)，會顯示錯誤訊息，請檢查網路或後端狀態。

---

## 應用範例

- 手動在 `training/1/academic.json` 中增補單字資料後，於程式中呼叫：
    ```python
    process_part_directory('./training/1')
    ```
  即可將 academic, calculus, ielts 等 .json 中的所有單字一併插入後端。

- 若後端 `/add-words` 實作支援部分成功寫入，其餘衝突跳過，程式會顯示 HTTP 409 資訊，代表有些已存在或重複。

---

## 注意事項

- 字典 API：`fetch_word_data()` 預設呼叫 `dictionary-api.eliaschen.dev`，若此服務暫停，需改用其他字典或本地化資料。
- JSON 結構：原始 `.json` 檔需為一個清單 (list)，每個元素帶有至少 `word` 欄位，其餘欄位如 `pos, meaning` 可選。
- API 衝突：若後端檢查到同樣 part/topic/word 已存在，可能回傳 409 (Conflict)。
- 多次呼叫：`InsertWordsAPI.py` 沒有 state 管理機制，如同一資料重複執行，可能導致重複插入(若後端無判重機制)或 409 衝突。

--- 

## 結語

`manual_insert_word` 資料夾是用於**手動**地將批量字詞插入到後端資料庫的重要工具。

- 你可以視需求修訂 JSON 檔案內容或指定 part / topic，並輕鬆透過 `InsertWordsAPI.py` 進行大量字詞資料的匯入。
- 相關程式中亦提供了從外部字典 API 獲取補充資訊的能力，使字詞內容更豐富完善。

## 授權與貢獻

- 本專案採用 Apache 授權
- 歡迎提交 Issues、Pull Requests 改進此自動爬蟲流程！