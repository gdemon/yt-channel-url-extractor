# Project Context: yt-channel-url-extractor (YouTube 最新影片擷取器)

## 🎯 1. 專案目標與核心商業邏輯 (Project Overview)
- **核心目標**：建立一支輕量化的自動化腳本，給定任意 YouTube 頻道或播放清單網址，能自動檢查並提取「今日最新發佈」的影片網址。若今日無新影片，則安全地回傳空值或提示。
- **主要策略**：避免使用官方 YouTube Data API（免除 API Key 限制與額度問題），並透過開源工具 `yt-dlp` 直接解析網頁 Metadata。
- **預期行為**：需具備高效率與精準度，透過混合式抓取策略（快速獲取整體清單 + 針對頭尾影片做深度檢驗）來確保正確抓取 `upload_date`，並能相容不同排序邏輯的自訂 Playlist。

## 🛠️ 2. 技術棧與環境 (Tech Stack & Environment)
- **主要語言**：Python 3.x
- **核心套件**：
  - 影片 Metadata 解析：`yt-dlp`
- **運行環境**：Windows 本地端執行（提供 `extract.bat` 作為入口腳本），依賴 Python 的虛擬環境 (`venv`)。

## 📂 3. 核心目錄結構 (Directory Structure)
- `main.py`：核心業務邏輯，包含抓取播放清單、過濾候選影片，以及檢查上傳日期的程式碼。
- `asr_converter.py`：本機端 Whisper 語音轉譯程式，依賴 `faster-whisper` 來達到極速 GPU 轉換。
- `run_pipeline.py`：最高階的一鍵執行流水線，自動整合 `main.py` 與 `asr_converter.py` 處理下載並轉譯流程。
- `run_pipeline_url.py`：直接傳入單一 YouTube 影片網址，略過頻道檢查每日影片環節，直接下載並轉譯的腳本。
- `extract.bat`：Windows 下的快速啟動批次檔，會自動 source 虛擬環境並執行帶有目標 URL 的 Python 腳本。
- `requirements.txt`：專案套件依賴清單。
- `/venv/`：由使用者自行建置的 Python 虛擬環境目錄。

## ✍️ 4. 程式碼規範與偏好 (Coding Conventions)
1. **防呆與異常處理 (Error Handling)**：對 `yt-dlp` 的操作必須包裝在 `try-except` 或安全的迴圈捕捉中。如果解析單一部影片發生錯誤，應記錄(或略過)並繼續檢查下一部，不可讓整個程式崩潰。
2. **型別提示 (Type Hinting)**：Python 函式需維持清晰的 Type Hints（例如 `def get_today_latest_video_url(url: str) -> str:`）。
3. **註解與說明**：核心過濾邏輯（如處理 Playlist 頭尾機制）需保留繁體中文註解。
4. **維持輕量化**：避免引入不必要的大型第三方依賴或資料庫模組，維持作為「單兵作業腳本」的純粹性。

## ⚠️ 5. 已知問題與特殊注意事項 (Known Issues & Notes)
- **`yt-dlp` 的 Metadata 限制**：針對 YouTube 播放清單（Playlist），`yt-dlp` 使用 `extract_flat=True` 快速抓取時，通常無法解析出真實的 `upload_date`。因此必須先取得長列表後，再針對最前 5 部與最後 5 部「候選名單」設定 `extract_flat=False` 以獲取真實的 Metadata 日期。
- **清單排序差異**：YouTube 頻道預設的影片列表通常是「由新到舊」，但使用者自訂或某些官方 Playlist 可能是「由舊到新」增加。因此腳本必須頭尾雙向檢查。
- **避免封鎖**：程式已設置 `quiet: True` 和 `no_warnings: True` 降低終端機噪音。過度頻繁地對同一個 Playlist 做 Deep Extraction（`extract_flat=False`）可能觸發 YouTube 暫時封鎖，目前只取 10 個候選者的策略是為效能與防封鎖的最佳化。