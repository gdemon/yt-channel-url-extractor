import sys
import yt_dlp
from datetime import datetime
import argparse

class YTDLPQuietLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        if "Private video" in msg:
            pass
        else:
            print(msg, file=sys.stderr)

def get_today_latest_video_url(url: str, cookies: str = None, cookies_from_browser: str = None) -> str:
    """
    Extract the latest video URL from a YouTube channel or playlist if it was published today.
    """
    import os
    # 步驟一：使用 extract_flat 快速取得頻道或播放清單的所有影片結構
    ydl_opts_flat = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
        'logger': YTDLPQuietLogger(),
    }
    if cookies:
        ydl_opts_flat['cookiefile'] = cookies
    elif cookies_from_browser:
        ydl_opts_flat['cookiesfrombrowser'] = (cookies_from_browser,)
    elif os.path.exists('cookies.txt'):
        ydl_opts_flat['cookiefile'] = 'cookies.txt'
    
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
        'logger': YTDLPQuietLogger(),
    }
    if cookies:
        ydl_opts_detail['cookiefile'] = cookies
    elif cookies_from_browser:
        ydl_opts_detail['cookiesfrombrowser'] = (cookies_from_browser,)
    elif os.path.exists('cookies.txt'):
        ydl_opts_detail['cookiefile'] = 'cookies.txt'
    
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
    parser.add_argument("--cookies", help="Path to cookies file (e.g. cookies.txt)")
    parser.add_argument("--cookies-from-browser", help="Browser to extract cookies from (e.g. chrome, firefox, edge)")
    args = parser.parse_args()
    
    video_url = get_today_latest_video_url(
        args.channel_url,
        cookies=args.cookies,
        cookies_from_browser=args.cookies_from_browser
    )
    
    if video_url:
        print(video_url)
        if args.download:
            import os
            print("開始下載音檔...", file=sys.stderr)
            ydl_opts_download = {
                'format': '251/bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': False,
                'no_warnings': True,
            }
            if args.cookies:
                ydl_opts_download['cookiefile'] = args.cookies
            elif args.cookies_from_browser:
                ydl_opts_download['cookiesfrombrowser'] = (args.cookies_from_browser,)
            elif os.path.exists('cookies.txt'):
                ydl_opts_download['cookiefile'] = 'cookies.txt'
            try:
                with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                    ydl.download([video_url])
                print("音檔下載完成！", file=sys.stderr)
            except Exception as e:
                print(f"下載失敗: {e}", file=sys.stderr)
    else:
        print("今天該頻道/清單沒有發佈最新影片，或查無資料。", file=sys.stderr)
