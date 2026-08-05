import os
import sys
import yt_dlp

from asr_converter import convert_audio_to_text

def run_pipeline_url(video_url, cookies=None, cookies_from_browser=None):
    print(f"Starting download for video URL: {video_url}")
    
    # 設定下載參數 (優先使用 251 format，遇 403 障礙時自動 fallback 至 bestaudio)
    ydl_opts_download = {
        'format': '251/bestaudio/best',
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
        # download=True 順便下載檔案並取得詳細資訊
        info = ydl.extract_info(video_url, download=True)
        
        # 取得 yt_dlp 實際在本地儲存的檔名
        if 'requested_downloads' in info:
            downloaded_file = info['requested_downloads'][0]['filepath']
        else:
            downloaded_file = ydl.prepare_filename(info)
            
    print(f"\nDownload complete! File saved at: {downloaded_file}")
    print("Starting ASR conversion...")
    
    # 呼叫同一層目錄的 asr_converter
    convert_audio_to_text(downloaded_file)
    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="直接下載單一 YouTube 影片網址並進行 ASR 轉譯。")
    parser.add_argument("youtube_video_url", help="Youtube 影片網址")
    parser.add_argument("--cookies", help="Path to cookies file (e.g. cookies.txt)")
    parser.add_argument("--cookies-from-browser", help="Browser to extract cookies from (e.g. chrome, firefox, edge)")
    args = parser.parse_args()
    
    run_pipeline_url(args.youtube_video_url, cookies=args.cookies, cookies_from_browser=args.cookies_from_browser)
