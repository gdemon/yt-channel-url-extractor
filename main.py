import sys
import yt_dlp
from datetime import datetime
import argparse

def get_today_latest_video_url(url: str) -> str:
    """
    Extract the latest video URL from a YouTube channel or playlist if it was published today.
    """
    # 步驟一：使用 extract_flat 快速取得頻道或播放清單的所有影片結構
    ydl_opts_flat = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
    }
    
    today_str = datetime.now().strftime('%Y%m%d')
    entries = []
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                entries = list(info['entries'])
            else:
                entries = [info]
    except Exception as e:
        print(f"解析發生錯誤: {e}", file=sys.stderr)
        return None
        
    if not entries:
        return None
        
    # 因為頻道最新影片通常在「最前面」(index 0)
    # 而有些手動維護的播放清單最新影片會放在「最後面」(index -1)
    # 為了確保都能抓到，我們從清單的最前 5 部與最後 5 部影片來做深入檢查
    candidates = []
    if len(entries) <= 10:
        candidates = entries
    else:
        # 將最後 5 部反轉順序 (優先檢查最後一個)，再加上最前面的 5 部
        candidates = entries[-5:][::-1] + entries[:5]
        
    # 步驟二：對候選影片進行深入解析以取得真實的 upload_date
    ydl_opts_detail = {
        'extract_flat': False,
        'quiet': True,
        'no_warnings': True,
    }
    
    latest_today_video = None
    
    with yt_dlp.YoutubeDL(ydl_opts_detail) as ydl:
        for entry in candidates:
            if not entry:
                continue
                
            video_url = entry.get('url') or entry.get('webpage_url')
            if not video_url:
                continue
                
            # 部分 extract_flat 結果只會給 ID
            if not video_url.startswith('http'):
                video_url = f"https://www.youtube.com/watch?v={video_url}"
                
            try:
                # 取得該部影片的詳細 Metadata
                v_info = ydl.extract_info(video_url, download=False)
                upload_date = v_info.get('upload_date')
                
                # 比對上傳日期是否為今日
                if upload_date == today_str:
                    latest_today_video = v_info.get('webpage_url', video_url)
                    break 
            except Exception:
                continue

    return latest_today_video

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="給定 Youtube 頻道或清單網址，若最新影片為今日發佈則抓出其網址。")
    parser.add_argument("channel_url", help="Youtube 網址 (例如頻道或播放清單)")
    parser.add_argument("-d", "--download", action="store_true", help="若今日有新影片，自動下載其音檔 (format 251)")
    args = parser.parse_args()
    
    video_url = get_today_latest_video_url(args.channel_url)
    
    if video_url:
        print(video_url)
        if args.download:
            print("開始下載音檔...", file=sys.stderr)
            ydl_opts_download = {
                'format': '251',
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': False,
                'no_warnings': True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                    ydl.download([video_url])
                print("音檔下載完成！", file=sys.stderr)
            except Exception as e:
                print(f"下載失敗: {e}", file=sys.stderr)
    else:
        print("今天該頻道/清單沒有發佈最新影片，或查無資料。", file=sys.stderr)
