# YouTube 機器人驗證與 Cookie 使用指南 (YouTube Bot Detection & Cookies Guide)

當您在使用 `yt-dlp` 解析或下載 YouTube 影片時，可能會遇到類似以下的錯誤訊息：
```
ERROR: [youtube] OwP0EqPgFBw: Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies for the authentication.
```
這是因為 YouTube 偵測到您的 IP 存取行為異常（例如使用 VPN、短時間請求過多、或是被判定為機器人）。此時，您必須提供登入後的 Cookie 讓 `yt-dlp` 以您的瀏覽器身份來存取。

本專案已支援多種簡便的 Cookie 帶入機制，以下是使用說明。

---

## 🛠️ 使用方法 (Usage Methods)

本專案支援三種傳遞 Cookie 的機制：

### 方法一：全自動偵測 `cookies.txt` (推薦)
1. **取得 Cookie 檔案**：
   * 在 Chrome 或 Firefox 安裝擴充套件，例如 **「Get cookies.txt LOCALLY」**。
   * 開啟 YouTube 網頁並確認您已登入。
   * 使用該套件點擊「Export」，將 Cookie 匯出為 **Netscape 格式** 的文字檔。
2. **放置檔案**：
   * 將下載的 Cookie 檔案重新命名為 `cookies.txt`。
   * 將它放置在本專案的根目錄下 (`yt-channel-url-extractor/cookies.txt`)。
3. **執行**：
   * 當專案的指令偵測到根目錄有 `cookies.txt` 時，將會**自動載入**，您不需要修改任何命令或新增任何 Flag。
   * *注意：`cookies.txt` 已被設定於 `.gitignore` 中，您的個人憑證不會被上傳至 Git 倉庫。*

### 方法二：使用瀏覽器的 Cookies (`--cookies-from-browser`)
如果您不想手動匯出 Cookie，可以讓 `yt-dlp` 直接從您本機的瀏覽器中讀取：
* **適用瀏覽器**：`chrome`, `firefox`, `edge`, `safari`, `opera`, `brave` 等。
* **使用語法**：
  * **主程式 (main.py)**:
    ```bash
    python main.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST" --cookies-from-browser chrome
    ```
  * **完整流水線 (run_pipeline.py / run_pipeline_api.py)**:
    ```bash
    python run_pipeline.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST" --cookies-from-browser chrome
    # 或使用 API 版本
    python run_pipeline_api.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST" --cookies-from-browser chrome
    ```
  * **直接轉譯影片 (run_pipeline_url.py)**:
    ```bash
    python run_pipeline_url.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies-from-browser chrome
    ```
* *注意：執行命令時，請先關閉該瀏覽器，否則 `yt-dlp` 可能會因為瀏覽器資料庫被鎖定 (Lock) 而無法讀取 Cookie。*

### 方法三：指定任意路徑的 Cookie 檔案 (`--cookies`)
如果您將 Cookie 檔案存放在其他地方，可以使用 `--cookies` 參數手動指定路徑：
```bash
python main.py "https://www.youtube.com/@YouTube" --cookies "C:\path\to\my_cookies.txt"
```

---

## ⚠️ 安全注意事項 (Security Warning)
* **請勿分享您的 Cookie 檔案**：Cookie 包含您的 YouTube 帳戶登入憑證。取得該檔案的任何人都可以直接登入您的帳戶。
* **定期更新**：YouTube 的 Cookie 通常有時效性。如果過了一陣子又出現 bot 錯誤，請重新匯出並替換 `cookies.txt`。
