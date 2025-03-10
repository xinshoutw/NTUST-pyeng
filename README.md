# NTUST 英簡單

> 網站: [NTUST 英簡單](https://ntust-eng.xinshou.tw/)

這是一個以 **Next.js + Tailwind CSS** 打造的前端專案，提供英文字卡學習與測驗功能，後端部分則由 **Python** 服務來支援資料庫與
API。
本專案原始碼結構如上，可粗略分為前端 (app / components / public) 以及後端 (python-backend) 兩大區塊。

## 專案結構總覽

```bash
.
├── README.md                # 你現在所閱讀的檔案
├── app/                     # Next.js 13 新的 App Router，主要頁面與佈局
│   ├── practice/            # Practice 頁面路由
│   ├── types.ts             # 前端 types 定義
│   └── utils.ts             # 前端呼叫後端 API 的輔助函式
├── components/              # 可重用元件，如WordCard, WordsGrid等
├── public/                  # 靜態檔案 (icons, images)
├── python-backend/          # Python後端專案資料夾
│   ├── auto_fetch_practice/ 
│   ├── backend/
│   ├── manual_insert_word/
│   └── web_demo/
│       ├── README.md
│       ├── app.py
│       └── start.sh
├── tailwind.config.js
└── tsconfig.json
```

- `app/`
    - `page.tsx`：首頁 (顯示字卡列表)。
    - `practice/page.tsx`：測驗頁面。
    - `layout.tsx`：全域佈局(Layout)。
    - `globals.css`：全域樣式（Tailwind, global CSS）。

- `components/`
    - `WordsGrid.tsx`：顯示字卡清單、篩選邏輯。
    - `WordCard.tsx`：單字卡片的呈現與動畫。
    - `PracticeClient.tsx`：客戶端測驗邏輯。
    - `Dropdown.tsx`：可重用的下拉式選單。
    - `ThemeToggleButton.tsx`：切換暗/亮主題的按鈕。
    - `Footer.tsx`：底部區域。

- `python-backend/`
    - `auto_fetch_practice/`：自動化抓取練習題目的工具程式。
    - `backend/`：後端核心程式，如 app.py (FastAPI)、資料庫操作、模型與結構等。
    - `manual_insert_word/`：手動插入英文字的工具。
    - `web_demo/`：示範或測試用途的簡易後端程式。

### 其他檔案

- `public/`：網頁 icon / 圖示，直接對外提供的靜態資源。
- `tailwind.config.js` / `postcss.config.js`：Tailwind 及 PostCSS 設定。
- `tsconfig.json`：TypeScript 設定。
- `package.json` / `package-lock.json`：前端相依套件資訊。

## Python 後端說明

關於 **Python** 服務（`python-backend/` 資料夾）各自的功能與使用教學，請前往各資料夾內的 README.md 了解詳細資訊，如檔案功能、部署方式、環境需求等。

## 前端啟動方式 (開發)

### 安裝依賴套件

```bash
npm install
```

### 啟動開發伺服器。

- 預設在 http://localhost:3000 瀏覽。
  ```bash
  npm run dev
  ```

### 打包 (Build)。

- 產生 production 版。
  ```bash
  npm run build
  ```

### 正式環境執行。

- 即可在本地執行 prod 版。
  ```bash
  npm run start
  ```

## 部署與其他說明

若要將前端部署在 GitHub Pages 或 Cloudflare Pages，請參考前端建置輸出的靜態檔案做部署設定。
若要查看 Python 後端的執行方式，請參考 python-backend/ 下各子資料夾的教學。

## 授權與貢獻

- 本專案採用 Apache 授權
- 歡迎提交 Issues、Pull Requests 改進此自動爬蟲流程！
