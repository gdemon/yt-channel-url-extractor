import os
import sys
import yt_dlp

from main import get_today_latest_video_url
from asr_converter import convert_audio_to_text

def run_pipeline(url):
    print(f"Checking URL: {url}")
    video_url = get_today_latest_video_url(url)
    
    if not video_url:
        print("No new video published today. Exiting.")
        return
        
    print(f"Found latest video: {video_url}")
    print("Starting download...")
    
    # 設定下載參數 (使用回原本的 251 format)
    ydl_opts_download = {
        'format': '251',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': True,
    }
    
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
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <youtube_url>")
        sys.exit(1)
        
    url = sys.argv[1]
    run_pipeline(url)
