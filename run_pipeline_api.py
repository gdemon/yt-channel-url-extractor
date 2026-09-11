import os
import sys
import yt_dlp
import subprocess

from main import get_today_latest_video_url

def run_pipeline_api(url, output_dir=None, cookies=None, cookies_from_browser=None, lang="zh-TW", workers=5, chunk_size=30000):
    output_dir = output_dir or os.environ.get("OUTPUT_DIR")
    if output_dir:
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory: {output_dir}", flush=True)

    print(f"Checking URL: {url}", flush=True)
    video_url = get_today_latest_video_url(url, cookies=cookies, cookies_from_browser=cookies_from_browser)
    
    if not video_url:
        print("No new video published today. Exiting.", flush=True)
        return
        
    print(f"Found latest video: {video_url}", flush=True)
    
    outtmpl_pattern = os.path.join(output_dir, '%(title)s.%(ext)s') if output_dir else '%(title)s.%(ext)s'

    # 設定下載參數 (優先使用 251 format，遇 403 障礙時自動 fallback 至 bestaudio)
    ydl_opts_download = {
        'format': '251/bestaudio/best',
        'outtmpl': outtmpl_pattern,
        'quiet': False,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    if cookies:
        ydl_opts_download['cookiefile'] = cookies
    elif cookies_from_browser:
        ydl_opts_download['cookiesfrombrowser'] = (cookies_from_browser,)
    elif os.path.exists('cookies.txt'):
        ydl_opts_download['cookiefile'] = 'cookies.txt'
        
    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
        # 先取得詳細資訊 (download=False) 以計算預期的檔名
        info = ydl.extract_info(video_url, download=False)
        expected_file = ydl.prepare_filename(info)
        
    base_name = os.path.splitext(expected_file)[0]
    txt_file = base_name + ".txt"

    # 檢查是否已存在已下載的音訊或影片檔
    existing_file = None
    if os.path.exists(expected_file):
        existing_file = expected_file
    else:
        for ext in ['.webm', '.mp4', '.m4a', '.opus', '.mkv']:
            candidate = base_name + ext
            if os.path.exists(candidate):
                existing_file = candidate
                break

    if existing_file:
        if os.path.exists(txt_file):
            print(f"Latest audio file ({existing_file}) and transcript ({txt_file}) already exist. Skipping to avoid redundant effort.", flush=True)
            return
        else:
            print(f"Latest audio file already exists: {existing_file}. Skipping download and proceeding to ASR conversion.", flush=True)
            downloaded_file = existing_file
    else:
        print("Starting download...", flush=True)
        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
            # download=True 順便下載檔案並取得詳細資訊
            info = ydl.extract_info(video_url, download=True)
            
            # 取得 yt_dlp 實際在本地儲存的檔名
            if 'requested_downloads' in info:
                downloaded_file = info['requested_downloads'][0]['filepath']
            else:
                downloaded_file = expected_file
                
        print(f"\nDownload complete! File saved at: {downloaded_file}", flush=True)

    print("Starting ASR conversion via Google Speech Recognition API...", flush=True)
    
    # 呼叫同一層目錄下的 scripts/transcribe_api.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "transcribe_api.py")
    if not os.path.exists(script_path):
        print(f"Error: ASR script not found at {script_path}", file=sys.stderr, flush=True)
        sys.exit(1)
        
    cmd = [
        sys.executable,
        "-u",
        script_path,
        "-i", downloaded_file,
        "-l", lang,
        "-w", str(workers),
        "-c", str(chunk_size)
    ]
    
    print(f"Executing: {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"\nASR transcription failed with return code {result.returncode}", file=sys.stderr, flush=True)
        sys.exit(result.returncode)
        
    print("\nPipeline completed successfully!", flush=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="一鍵執行 YouTube 影片下載與 Google Speech API ASR 轉譯管線。")
    parser.add_argument("youtube_url", help="Youtube 頻道或播放清單網址")
    parser.add_argument("-o", "--output-dir", help="輸出音訊與逐字稿目錄 (預設為當前目錄，或環境變數 OUTPUT_DIR)")
    parser.add_argument("--cookies", help="Path to cookies file (e.g. cookies.txt)")
    parser.add_argument("--cookies-from-browser", help="Browser to extract cookies from (e.g. chrome, firefox, edge)")
    parser.add_argument("--lang", default="zh-TW", help="Language code (default: zh-TW)")
    parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers (default: 5)")
    parser.add_argument("--chunk-size", type=int, default=30000, help="Chunk length in milliseconds (default: 30000)")
    args = parser.parse_args()
    
    run_pipeline_api(
        args.youtube_url, 
        output_dir=args.output_dir,
        cookies=args.cookies, 
        cookies_from_browser=args.cookies_from_browser,
        lang=args.lang,
        workers=args.workers,
        chunk_size=args.chunk_size
    )
