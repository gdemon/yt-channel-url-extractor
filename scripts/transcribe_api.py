import os
import sys
import shutil
import time
import random
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydub import AudioSegment
from pydub.utils import make_chunks
import speech_recognition as sr

# Reconfigure stdout/stderr to UTF-8 to prevent UnicodeEncodeError on Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_dependencies():
    # Check if ffmpeg is in path
    if not shutil.which("ffmpeg") and not shutil.which("ffmpeg.exe"):
        print("Error: 'ffmpeg' was not found on your system PATH.", file=sys.stderr)
        print("Please ensure FFmpeg is installed and added to your PATH.", file=sys.stderr)
        return False
    return True

def transcribe_chunk(chunk_path, chunk_index, total_chunks, language="zh-TW", max_retries=3):
    recognizer = sr.Recognizer()
    for attempt in range(max_retries):
        try:
            with sr.AudioFile(chunk_path) as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=language)
            print(f"[{chunk_index + 1}/{total_chunks}] Success")
            return chunk_index, text
        except sr.UnknownValueError:
            print(f"[{chunk_index + 1}/{total_chunks}] Silent or unintelligible")
            return chunk_index, ""
        except sr.RequestError as e:
            print(f"[{chunk_index + 1}/{total_chunks}] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))
            else:
                return chunk_index, f" [Transcription Error: {e}] "
        except Exception as e:
            print(f"[{chunk_index + 1}/{total_chunks}] Error: {e}")
            return chunk_index, f" [Error: {e}] "

def main():
    parser = argparse.ArgumentParser(description="Audio Transcription (ASR) Tool using Google Speech Recognition API")
    parser.add_argument("-i", "--input", required=True, help="Path to the input audio file (e.g., MP3)")
    parser.add_argument("-o", "--output", help="Path to the output text file (defaults to replacing file extension with .txt)")
    parser.add_argument("-l", "--lang", default="zh-TW", help="Language code (default: zh-TW)")
    parser.add_argument("-w", "--workers", type=int, default=5, help="Number of parallel workers (default: 5)")
    parser.add_argument("-c", "--chunk-size", type=int, default=30000, help="Chunk length in milliseconds (default: 30000)")

    args = parser.parse_args()

    if not check_dependencies():
        sys.exit(1)

    mp3_path = os.path.abspath(args.input)
    if not os.path.exists(mp3_path):
        print(f"Error: Input file does not exist: {mp3_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        output_path = os.path.splitext(mp3_path)[0] + ".txt"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(script_dir, "temp_chunks")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        print("Loading audio file...")
        audio = AudioSegment.from_file(mp3_path)
        
        print("Chunking audio...")
        chunks = make_chunks(audio, args.chunk_size)
        total_chunks = len(chunks)
        print(f"Created {total_chunks} chunks.")

        print("Exporting chunks to WAV files...")
        chunk_paths = []
        for idx, chunk in enumerate(chunks):
            chunk_path = os.path.join(temp_dir, f"chunk_{idx}.wav")
            chunk.export(chunk_path, format="wav")
            chunk_paths.append(chunk_path)
        
        print(f"Starting transcription using Google Speech Recognition API ({args.lang}) with {args.workers} workers...")
        results = {}
        
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(transcribe_chunk, path, idx, total_chunks, args.lang): idx 
                for idx, path in enumerate(chunk_paths)
            }
            for future in as_completed(futures):
                idx, text = future.result()
                results[idx] = text

        full_transcript = []
        for idx in range(total_chunks):
            text = results.get(idx, "")
            if text.strip():
                full_transcript.append(text)
        
        final_text = "\n".join(full_transcript)
        
        print(f"Saving transcript to {output_path}...")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_text)
            
    except Exception as e:
        print(f"An unexpected error occurred during transcription: {e}", file=sys.stderr)
    finally:
        print("Cleaning up temporary chunk files...")
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Failed to clean up temp dir: {e}", file=sys.stderr)
            
    print("Done!")

if __name__ == "__main__":
    main()
