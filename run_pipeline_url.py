import os
import sys
import yt_dlp

from asr_converter import convert_audio_to_text

def run_pipeline_url(video_url):
    print(f"Starting download for video URL: {video_url}")
    
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
        print("Usage: python run_pipeline_url.py <youtube_video_url>")
        sys.exit(1)
        
    video_url = sys.argv[1]
    run_pipeline_url(video_url)
