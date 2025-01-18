# Main Backend

此資料夾為後端核心程式，使用 FastAPI + SQLAlchemy + SQLite 搭建。主要提供下列功能：

1. RESTful API 供前端或其他服務串接
2. 單字/練習題的增刪查改
3. JWT 或 Bearer Token 驗證
4. 基礎資料庫 (SQLite) 操作

---

## 檔案結構

```bash
backend/
├── README.md       # 你現在所閱讀的檔案
├── app.py          # 主要後端啟動檔案 (FastAPI 入口)
├── data.db         # SQLite 資料庫檔案 (若使用預設資料庫)
├── database.py     # SQLAlchemy Engine 及 Session 連線設定
├── models.py       # 定義資料表 (Entry, Choice, Word)
├── schemas.py      # Pydantic 資料驗證模型
└── start.sh        # (可選) 啟動伺服器的指令腳本
```

- `app.py`
    - 使用 FastAPI 作為框架
    - 重要區塊：
        - 環境變數：載入 `.env` 以取得 `HOST`, `PORT`, `BEARER_TOKEN`, 以及 CORS 設定
        - CORS 設定：可在 `ALLOWED_ORIGINS` 加入白名單
        - 路由：各項 API 如 `GET /api/words`, `POST /api/add-words`, `GET /api/practice/{part}/{topic}`等
        - 驗證機制：`verify_bearer_token` 會檢查來自瀏覽器/客戶端的 Bearer Token 與伺服器設定相符與否
        - 例外處理：對 HTTP 例外、驗證錯誤、通用錯誤做統一回應
        - main 區塊：使用 `uvicorn.run` 啟動伺服器
- `database.py`
    - `create_engine`：連線至 `sqlite:///./data.db` (預設)
    - `SessionLocal`：提供資料庫操作的 Session 物件
    - `Base(DeclarativeBase)`：SQLAlchemy ORM Base 類別，用於在 models.py 定義資料表
    - 外鍵約束：`PRAGMA foreign_keys=ON;` 用於 SQLite 啟用外鍵
- `models.py`
    - 定義資料庫的 ORM Model：
        - Entry：用於練習題的主表 (question, answer, part, topic...)
        - Choice：對應到練習題各個選項 (外鍵連到 `entries.id`)
        - Word：存放單字 (part, topic, word, meaning...)
    - 皆使用 SQLAlchemy 新版 `Mapped` 語法
- `schemas.py`
    - Pydantic 驗證及序列化模型：
        - PracticeResponse, TopicsResponse, PartResponse...
        - AddWordsRequestSchema, AddWordsResponseSchema：新增單字時的請求與回應格式
        - AddPracticesRequestSchema, AddPracticesResponseSchema：新增練習題目時的請求/回應格式
        - WordSchema, DefinitionSchema, PronunciationSchema 等詳細字詞結構
- `start.sh`
    - (可選) 可以在此放啟動指令，如 `uvicorn app:app --host 0.0.0.0 --port 8000` 或 docker run 指令
    - 也可整合 `tmux`, `screen` 或 `pm2` 等進行常駐運行

---

## 環境變數

常用的 `.env` 參數包括：

- HOST：伺服器監聽 IP (預設 `0.0.0.0`)
- PORT：伺服器監聽 Port (預設 `8000`)
- BEARER_TOKEN：後端接受的 Token，用於保護 `/api/add-words` 等路由
- ALLOWED_ORIGINS：CORS 白名單，允許的前端域名列表 (逗號分隔)

也可在系統環境變數中設置或於 `.env` 檔案中定義。

--- 

## 啟動 / 使用方式

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 建立 .env (可選)

```bash
HOST=0.0.0.0
PORT=8000
BEARER_TOKEN=abc123
ALLOWED_ORIGINS=http://localhost:3000
```

### 執行

```bash
python app.py
# 或使用 uvicorn:
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 測試

- 開啟瀏覽器訪問 `http://127.0.0.1:8000/heartbeat` ，應回傳 `{"status":"ok"}`
- 使用 Postman / curl 測試 `/api/words` 或 `/api/practice/{part}/{topic}`
- 確保需要 Token 的路由 (如 `/api/add-words`) 要在 header 帶 `Authorization: Bearer abc123`

---

## 常見路由

### 健康檢測

- `GET /heartbeat` → 回傳 `{ "status": "ok" }`

### 取得單字

- `GET /api/words?part=1&topic=calculus`
- 透過 Query 參數篩選 part, topic

### 新增單字

- `POST /api/add-words`
- 需提供 Bearer Token
- Body 為 `AddWordsRequestSchema` 格式：
    ```json
    {
      "words": [
        {
          "part": 1,
          "topic": "calculus",
          "word": "derivative",
          "pos": "n",
          "meaning": "導數"
        }
      ]
    }
    ```

### 取得練習題

- `GET /api/practice/{part}/{topic}` → 回傳題目、選項

### 新增練習題

- `POST /api/add-practices?part=1&topic=calculus`
- Body 為 AddPracticesRequestSchema 格式

---

## 注意事項

- 預設使用 SQLite (`data.db`)，若要改用其他資料庫，可在 `DATABASE_URL` 中設定對應引擎 (MySQL, PostgreSQL, ...)，並調整
  `create_engine`。
- Bearer Token 應妥善管理，避免洩漏，否則可能導致 API 被任意新增資料。
- 若要在正式環境運行，建議使用 `Gunicorn + uvicorn workers` 或 Docker 進行部署。

---

## 結語

`backend` 目錄提供了完整的 FastAPI 後端實作，包括資料庫模式 (models, schemas)、API 路由與授權保護。
若需進一步擴充（如更多欄位、更複雜的查詢）可在本基礎上客製化修改。歡迎在此基礎進行二次開發或與前端串接使用。

---

## 授權與貢獻

- 本專案採用 Apache 授權
- 歡迎提交 Issues、Pull Requests 改進此後端！
