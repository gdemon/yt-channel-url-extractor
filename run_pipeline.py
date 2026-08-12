import os
import sys
import yt_dlp

from main import get_today_latest_video_url
from asr_converter import convert_audio_to_text

def run_pipeline(url, cookies=None, cookies_from_browser=None):
    print(f"Checking URL: {url}")
    video_url = get_today_latest_video_url(url, cookies=cookies, cookies_from_browser=cookies_from_browser)
    
    if not video_url:
        print("No new video published today. Exiting.")
        return
        
    print(f"Found latest video: {video_url}")
    
    # 設定下載參數 (優先使用 251 format，遇 403 障礙時自動 fallback 至 bestaudio)
    ydl_opts_download = {
        'format': '251/bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
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
        
        if os.path.exists(expected_file):
            print(f"Latest audio file already exists: {expected_file}. Skipping to avoid redundant effort.")
            return
            
    print("Starting download...")
    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
        # download=True 順便下載檔案並取得詳細資訊
        info = ydl.extract_info(video_url, download=True)
        
        # 取得 yt_dlp 實際在本地儲存的檔名
        if 'requested_downloads' in info:
            downloaded_file = info['requested_downloads'][0]['filepath']
        else:
            downloaded_file = expected_file
            
    print(f"\nDownload complete! File saved at: {downloaded_file}")
    print("Starting ASR conversion...")
    
    # 呼叫同一層目錄的 asr_converter
    convert_audio_to_text(downloaded_file)
    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="一鍵執行 YouTube 影片下載與 ASR 轉譯管線。")
    parser.add_argument("youtube_url", help="Youtube 頻道或播放清單網址")
    parser.add_argument("--cookies", help="Path to cookies file (e.g. cookies.txt)")
    parser.add_argument("--cookies-from-browser", help="Browser to extract cookies from (e.g. chrome, firefox, edge)")
    args = parser.parse_args()
    
    run_pipeline(args.youtube_url, cookies=args.cookies, cookies_from_browser=args.cookies_from_browser)
