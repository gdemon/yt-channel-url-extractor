import sys
import os
import time

def convert_audio_to_text(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        sys.exit(1)
        
    print(f"Start processing file via Local Faster-Whisper (GPU Mode): {file_path}")
    
    # 動態載入 faster-whisper
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Error: faster-whisper library is not installed.")
        sys.exit(1)
        
    # 對應 user 在 Buzz 的參數：Model: Small, Task: Transcribe, Language: Chinese
    model_size = "small"
    
    print("Loading model into GPU...")
    # 使用 CUDA 與 float16 來極大化 3090 的效能
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    
    print("Transcribing...")
    start_time = time.time()
    
    # 進行轉錄
    segments, info = model.transcribe(
        file_path, 
        task="transcribe",
        language="zh", 
        beam_size=5
    )
    
    print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")
    
    base_name, _ = os.path.splitext(file_path)
    txt_file = f"{base_name}.txt"
    
    # 寫入 txt 檔案並同時在終端機顯示進度
    with open(txt_file, "w", encoding="utf-8") as f:
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            f.write(segment.text + "\n")
            
    end_time = time.time()
    print(f"\nLocal Whisper conversion successfully completed in {end_time - start_time:.2f} seconds!")
    print(f"Transcript correctly saved at: {txt_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    convert_audio_to_text(file_path)
