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

#### 3. 搭配 Cookie 驗證
若升級後仍遇到存取限制，請參考 [cookies_guide.md](file:///d:/project_git/yt-channel-url-extractor/doc/cookies_guide.md) 放置 `cookies.txt` 或加入 `--cookies-from-browser` 參數。
