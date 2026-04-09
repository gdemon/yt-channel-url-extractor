# 🔄 交接檔案 (Handoff Status)
> **最後更新時間**：2026-04-09 22:50 (每次結束 session 前請 AI 更新此時間與內容)

## 📌 1. 當前開發進度 (Current Status)
- **目前專注的任務**：將語音轉錄全面改為本機端 GPU 取向的 `faster-whisper` 加速轉換框架，並解決相關 Windows 依賴問題。
- **系統狀態**：腳印整合完畢，透過 `run_pipeline.py` 與 `fetch_podcast.py` 皆可自動執行取得新片或Podcast、下載並驅動本機端 GPU 高速產生 `txt` 逐字稿。CUDA 函式庫問題已獲得解決。

## ✅ 2. 上次 Session 完成的事項 (Completed in Last Session)
- **錯誤訊息抑制與優化 (本 Session 補充)**：
  - **略過 Private Video 警告**：為了解決 `yt-dlp` 在過濾候選清單時，遇到私人影片 (Private video) 會強迫在硬體主控台印出 `ERROR` 訊息的干擾問題，新增自定義 `YTDLPQuietLogger` 記錄器，精準過濾並隱藏該項錯誤，保持終端機輸出乾淨。

- **純本地化 GPU 語音轉譯與流水線重構 (先前 Session)**：
  - **核心轉換**：為了最大化利用使用者的 RTX 3090 顯卡並避開 Python 3.14 的 PyTorch 不穩定與 API 限制，毅然放棄私有 ASR API，全面改採 `faster-whisper` (CTranslate2) 為底層引擎，實現超高速本地化 GPU 轉錄。
  - **管線建立**：撰寫 `run_pipeline.py` 自動銜接 `main.py` 與 `asr_converter.py`，保持原始 `webm` 音軌並安全傳遞，不再仰賴 .bat 做字串擷取。
  - **結構重整**：排除原本綁定私有金鑰的疑慮後，將 `run_pipeline.py` 與 `asr_converter.py` 從 `my_priv_script` 深處移出至 Repo Root，成為專案的正式開源工具。
  - **細節優化**：完善了 `my_priv_script/test_download.bat` 的絕對路徑指標（`%~dp0`），讓使用者不論身處哪個子資料夾執行都不會強迫改變工作目錄 (wd)，且輸出會留在使用者當前操作地。
  - **文件同步**：對 `requirements.txt`、`README.md` (新增 Method 3) 及 `PROJECT_CONTEXT.md` (定義檔案職責) 完成了文件迭代維護。

- **Podcast 抓取重構與測試指令新增 (本 Session 補充)**：
  - **引數化網址**：修改了 `fetch_podcast.py`，將原本寫死的 RSS URL 改由 CLI 外部參數傳入，增加重用度。
  - **新增測試批次檔**：遵循專案規範在 `scripts/test/` 中新增 `test_podcast.bat`，可用於快速測試帶入目標網址至 `fetch_podcast.py` 進行下載與 ASR 轉換流程。

- **GPU 運行環境修復與警告抑制 (本 Session 補充)**：
  - **補齊 CUDA DLLs**：針對 `faster-whisper` (CTranslate2) 在 Windows 下找不到 `cublas64_12.dll` 導致的崩潰，將 `nvidia-cublas-cu12` 及 `nvidia-cudnn-cu12` 寫入 `requirements.txt`。同時於 `asr_converter.py` 寫入啟動邏輯，動態注入 pip site-packages 路徑至系統 `PATH`，實現免安裝全域 CUDA Toolkit 的隨插即用。
  - **清理終端機訊號**：在各腳本導入 `HF_HUB_DISABLE_SYMLINKS_WARNING=1` 以封鎖 HuggingFace Cache 系統在 Windows 沒有開發者權限時拋出的無意義警告，還給使用者乾淨的 Console 畫面。
## 📁 歷史更新 (Past Sessions)
- **新增下載功能**：
  - 於 `main.py` 增加 `-d` (`--download`) 選項自動透過 `yt-dlp` 下載純音頻以利後續處理。
  - 修改 `extract.bat` 允許傳遞 `%*` 參數。在 `scripts/test/` 新增 `test_download.bat`。
- **環境建置與結構建立**：
  - 建立 `requirements.txt` 加入 `yt-dlp` 依賴。
  - 編寫 `extract.bat` 提供 Windows 下一鍵自動啟動 `venv` 並帶入網址參數的便捷方式。
- **核心擷取邏輯開發 (`main.py`)**：
  - 實作了混合式抓取機制，設計「雙向候選捕捉」與 `extract_flat=False` 等機制。
- **文檔撰寫與專案情境更新**：
  - 完成 `README.md` 與 `PROJECT_CONTEXT.md`。

## 🚀 3. 下一步 / 待辦事項 (Next Steps / To-Do)
- [ ] **通知整合 (Notification Integration)**：考慮未來將抓取結果串接 Discord, Telegram 或 Line Notify，達到即時推播通知。
- [ ] **排程自動化 (Scheduling)**：可考慮加入 Windows 工作排程器 (Task Scheduler) 或 GitHub Actions 教學，讓此腳本能每日定時自動觸發。
- [ ] **多重 URL 支援**：未來若需一次檢查多個頻道，可將 `main.py` 擴充為讀取 `urls.txt` 並批次檢查。

## 🐛 4. 已知未解 Bug / 技術債 (Known Bugs & Technical Debt)
- **技術債 (效能限制)**：為了避開 YouTube 封鎖，目前只檢查頭尾各 5 部影片的詳細日期。如果該 Playlist 在一天內被塞入超過 5 部以上的舊影片或新影片（即極端更新狀況），可能會導致目標影片被擠出檢查範圍而漏抓。
- **技術債 (IP Rate Limiting)**：如果未來擴充為同時檢查幾百個頻道，`yt-dlp` 短時間內下載大量 Detailed Metadata 會有被 YouTube 暫時封鎖 IP 的風險，可能需要加入 `time.sleep()` 或代理池。
