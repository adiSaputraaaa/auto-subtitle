import whisper
import sys
import os

def main():
    # Mengecek apakah user memasukkan path video/audio saat menjalankan script
    if len(sys.argv) < 2:
        print("Penggunaan: uv run main.py <path_ke_file_video_atau_audio>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Memastikan file ada
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan.")
        sys.exit(1)

    # 1. Memuat Model (Download otomatis saat pertama kali dijalankan)
    # Pilihan model: 'tiny', 'base', 'small', 'medium', 'large', 'turbo'
    # 'turbo' adalah versi cepat dan cukup akurat. Jika VRAM/RAM kurang, gunakan 'base' atau 'small'.
    print("Memuat model Whisper (bisa memakan waktu jika baru pertama kali)...")
    model = whisper.load_model("turbo")

    # 2. Mulai proses transkripsi
    print(f"Mulai melakukan transkripsi untuk: {file_path}")
    print("Harap tunggu, proses ini bergantung pada durasi video dan kecepatan CPU/GPU kamu...")
    
    # transcribe() akan membaca audio dari video/audio yang diberikan
    result = model.transcribe(file_path)

    # 3. Menampilkan hasil teksnya
    print("\n" + "="*40)
    print(" HASIL TRANSKRIPSI (AUTO SUBTITLE)")
    print("="*40)
    print(result["text"])
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
