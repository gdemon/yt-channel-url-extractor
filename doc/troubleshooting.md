# YouTube 錯誤與障礙排除指南 (Troubleshooting Guide)

## 1. HTTP Error 403: Forbidden 錯誤

當執行 `test_download_api.bat` 或下載管線時遇到以下錯誤：
```text
yt_dlp.networking.exceptions.HTTPError: HTTP Error 403: Forbidden
yt_dlp.utils.DownloadError: ERROR: unable to download video data: HTTP Error 403: Forbidden
```

### 🔴 原因說明
YouTube 經常升級影音串流簽名（Cipher / Player JS / SABR Token 驗證機制）。當 `yt-dlp` 版本較舊，或是請求特定格式（如純音訊 `format 251`）受到限制時，YouTube 的影音 CDN (googlevideo.com) 會直接回傳 `403 Forbidden` 拒絕下載。

---

### 🟢 解決方案 (Solutions)

#### 1. 升級 `yt-dlp` 至最新版本 (最有效)
在虛擬環境中執行以下命令升級 `yt-dlp` 套件：
```cmd
.\venv\Scripts\python.exe -m pip install --upgrade yt-dlp
```
*註：`yt-dlp` 社群維護極為頻繁，遇到 403 錯誤時優先升級套件即可解決 90% 以上的問題。*

#### 2. 音訊格式自動退避 (Format Fallback)
專案內的核心腳本 (`run_pipeline_api.py`, `run_pipeline.py`, `run_pipeline_url.py`, `main.py`) 已統一將下載格式設定為：
```python
'format': '251/bestaudio/best'
```
這意味著：
- 系統會優先嘗試下載最高音質的 Opus 格式 (`251`)。
- 若 `251` 受到 YouTube 403 限制或無法取得，系統會自動退避 (Fallback) 至其他可用之最佳音訊格式 (`bestaudio`/`best`)，確保管線不中斷。

#### 3. 跨 Client 自動降級與獨立 Context (Player Client & Isolated Context)
專案的核心腳本 (`run_pipeline_api.py`, `run_pipeline.py`, `run_pipeline_url.py`, `main.py`) 已加入多層防禦：
- **Extractor Client 降級**：配置 `'extractor_args': {'youtube': {'player_client': ['android', 'web']}}`，當 Web 端的串流 URL 遭到 YouTube SABR / PoToken 限制回傳 403 時，會自動 switch 至 Android Player API 取得合法的媒體串流 URL。
- **Context 隔離**：將檔名預檢 (`download=False`) 與實際下載 (`download=True`) 拆為獨立的 `yt_dlp.YoutubeDL` 上下文，防止過期的串流 URL Token 重複使用導致的 403 錯誤。

#### 4. 搭配 Cookie 驗證
若升級後仍遇到存取限制，請參考 [cookies_guide.md](file:///d:/project_git/yt-channel-url-extractor/doc/cookies_guide.md) 放置 `cookies.txt` 或加入 `--cookies-from-browser` 參數。

---

## 2. 批次腳本與 ASR 轉譯管線執行常見問題 (Batch Scripts & ASR Pipeline)

### 1. 終端機長時間無進度輸出或看似凍結
- **原因**：Python 在被批次檔呼叫或標準輸出重導向時，預設會使用 block buffer，導致轉譯進度 (`[x/total] Success`) 直到整個執行結束前都不會印出。
- **解決方式**：
  - 批次腳本執行 Python 時加上 `-u` 引數（如 `python -u run_pipeline_api.py ...`）。
  - `transcribe_api.py` 已啟用 `line_buffering=True` 與即時 `flush=True`，確保每個 chunk 轉譯成功時即時印出進度。

### 2. 視窗閃退或無法看清執行結果
- **原因**：雙擊 `.bat` 執行時，若無 `pause`，腳本結束或遇到錯誤時 CMD 視窗會瞬間關閉。另外若未切換工作目錄，會導致檔案儲存於子目錄且找不到根目錄之 `cookies.txt`。
- **解決方式**：
  - 批次檔開頭加入 `cd /d "%~dp0\.."` 確保工作目錄為專案根目錄。
  - 批次檔結尾加入 `pause` 避免視窗自動關閉。

### 3. 已下載音訊但未轉譯成逐字稿 (.txt)
- **原因**：舊版邏輯若發現目標音訊已存在，會直接終止管線，導致若上次轉譯中斷時永遠無法自動補轉。
- **解決方式**：`run_pipeline_api.py` 已優化為：若音檔已存在但逐字稿 (`.txt`) 尚未生成，會自動跳過下載步驟，直接以現有音檔進行 ASR 轉譯；只有當音檔與逐字稿皆存在時才會完全跳過。
