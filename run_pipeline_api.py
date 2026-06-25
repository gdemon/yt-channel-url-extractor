import os
import sys
import yt_dlp
import subprocess

from main import get_today_latest_video_url

def run_pipeline_api(url, cookies=None, cookies_from_browser=None, lang="zh-TW", workers=5, chunk_size=30000):
    print(f"Checking URL: {url}")
    video_url = get_today_latest_video_url(url, cookies=cookies, cookies_from_browser=cookies_from_browser)
    
    if not video_url:
        print("No new video published today. Exiting.")
        return
        
    print(f"Found latest video: {video_url}")
    
    # 設定下載參數 (使用回原本的 251 format)
    ydl_opts_download = {
        'format': '251',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': True,
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
        
        if os.path.exists(expected_file):
            print(f"Latest audio file already exists: {expected_file}. Skipping to avoid redundant effort.")
            return
            
        print("Starting download...")
        # download=True 順便下載檔案並取得詳細資訊
        info = ydl.extract_info(video_url, download=True)
        
        # 取得 yt_dlp 實際在本地儲存的檔名
        if 'requested_downloads' in info:
            downloaded_file = info['requested_downloads'][0]['filepath']
        else:
            downloaded_file = expected_file
            
    print(f"\nDownload complete! File saved at: {downloaded_file}")
    print("Starting ASR conversion via Google Speech Recognition API...")
    
    # 呼叫同一層目錄下的 scripts/transcribe_api.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "transcribe_api.py")
    if not os.path.exists(script_path):
        print(f"Error: ASR script not found at {script_path}", file=sys.stderr)
        sys.exit(1)
        
    cmd = [
        sys.executable,
        script_path,
        "-i", downloaded_file,
        "-l", lang,
        "-w", str(workers),
        "-c", str(chunk_size)
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"\nASR transcription failed with return code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)
        
    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="一鍵執行 YouTube 影片下載與 Google Speech API ASR 轉譯管線。")
    parser.add_argument("youtube_url", help="Youtube 頻道或播放清單網址")
    parser.add_argument("--cookies", help="Path to cookies file (e.g. cookies.txt)")
    parser.add_argument("--cookies-from-browser", help="Browser to extract cookies from (e.g. chrome, firefox, edge)")
    parser.add_argument("--lang", default="zh-TW", help="Language code (default: zh-TW)")
    parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers (default: 5)")
    parser.add_argument("--chunk-size", type=int, default=30000, help="Chunk length in milliseconds (default: 30000)")
    args = parser.parse_args()
    
    run_pipeline_api(
        args.youtube_url, 
        cookies=args.cookies, 
        cookies_from_browser=args.cookies_from_browser,
        lang=args.lang,
        workers=args.workers,
        chunk_size=args.chunk_size
    )
