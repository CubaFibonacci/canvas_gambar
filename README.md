# 🎨 GestureCanvas (canvas_gambar)

> **AI Hand Gesture Air Canvas** — Aplikasi kanvas interaktif pintar berbasis Python, OpenCV, dan Google MediaPipe untuk menggambar di udara (*Air Drawing*) secara *real-time* langsung menggunakan kamera/webcam tanpa menyentuh layar maupun mouse!

---

## 📌 Daftar Isi
1. [Fitur Utama](#-fitur-utama)
2. [Persyaratan Sistem](#-persyaratan-sistem)
3. [Panduan Instalasi](#-panduan-instalasi)
4. [Cara Menjalankan Aplikasi](#-cara-menjalankan-aplikasi)
5. [Tutorial Cara Menggunakan](#-tutorial-cara-menggunakan)
   - [Langkah 1: Setup Posisi & Kamera](#1-setup-posisi--kamera)
   - [Langkah 2: Gesture Tangan (Air Gestures)](#2-panduan-gesture-tangan)
   - [Langkah 3: Memilih Warna (Left Toolbar)](#3-memilih-warna--ketebalan-left-toolbar)
   - [Langkah 4: Fitur & Efek (Right Toolbar)](#4-menggunakan-fitur--efek-right-toolbar)
6. [Pintasan Keyboard (Hotkeys)](#-pintasan-keyboard-hotkeys)
7. [Versi Web Browser (Tanpa Install Python)](#-versi-web-browser)
8. [Struktur Folder](#-struktur-folder)
9. [Troubleshooting / Solusi Kendala](#-troubleshooting--faq)

---

## ✨ Fitur Utama

- 🖐️ **Real-Time Hand Tracking**: Pelacakan 21 titik sendi tangan berpresisi tinggi dengan tampilan skeleton perak futuristik (*cyberpunk wireframe*).
- 🌈 **Palet Warna Lengkap & Rainbow Slider**: 16 warna preset siap pakai + *Hue Slider* vertikal untuk memilih warna kustom apa saja.
- ⚡ **Mode Interaktif Lengkap**:
  - **Draw Mode (`DRW`)**: Menggambar bebas di udara.
  - **Erase Mode (`ERS`)**: Menghapus goresan tertentu secara fleksibel.
  - **Move Mode (`MOV`)**: Memilih dan memindahkan objek coretan (misal: memindahkan gambar mahkota, kacamata, dsb).
- 🌟 **Efek Visual Keren**:
  - **Neon Glow (`GLOW`)**: Efek garis menyala bercahaya (*bloom glow*).
  - **Rainbow Brush (`RNBW`)**: Warna kuas berubah pelangi secara dinamis saat digerakkan.
  - **Mirror Mode (`MRR`)**: Gambar simetri dua sisi sekaligus (kiri & kanan).
  - **Dark Canvas (`FLL`)**: Latar belakang papan tulis hitam pekat untuk fokus berkarya.
- 💾 **Save & Undo**:
  - Simpan karya beresolusi tinggi langsung ke folder `saved/` format `.png`.
  - Tombol Undo bertingkat untuk membatalkan goresan yang salah.
- 🖱️ **Dukungan Dual-Input**: Bisa dikontrol penuh dengan **gerakan tangan di udara** maupun klik **mouse**.

---

## 💻 Persyaratan Sistem

- **Sistem Operasi**: Windows 10 / 11, macOS, atau Linux
- **Webcam / Kamera**: Bawaan laptop atau webcam eksternal USB
- **Python**: Versi 3.9, 3.10, atau 3.11 (Direkomendasikan Python 3.10 - 3.11)

---

## ⚙️ Panduan Instalasi

### 1. Clone Repositori
Buka terminal / Git Bash / Command Prompt, lalu clone proyek ini:
```bash
git clone https://github.com/CeyyCubaa/canvas_gambar.git
cd canvas_gambar
```

### 2. (Opsional tapi Disarankan) Buat Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependensi
Pasang seluruh library yang dibutuhkan:
```bash
pip install -r requirements.txt
```
*Isi dependensi:* `opencv-python`, `mediapipe`, `numpy`.

---

## 🚀 Cara Menjalankan Aplikasi

Pilih salah satu cara berikut yang paling nyaman:

### Cara 1: Menggunakan `run.bat` (Windows - Paling Praktis)
Cukup **klik dua kali** pada file:
```
run.bat
```
Skrip ini akan otomatis mendeteksi instalasi Python dan langsung membuka aplikasi.

### Cara 2: Melalui Terminal / Command Prompt
Jalankan perintah berikut di folder proyek:
```bash
python main.py
```

---

## 📖 Tutorial Cara Menggunakan

### 1. Setup Posisi & Kamera
1. Pastikan ruangan memiliki **pencahayaan yang cukup** agar kamera dapat mendeteksi tangan dengan jelas.
2. Duduk berjarak sekitar **0.5 – 1.5 meter** dari webcam.
3. Arahkan telapak tangan ke depan kamera sampai muncul **kerangka kawat silver (hand landmark)** di layar.

---

### 2. Panduan Gesture Tangan

Aplikasi membaca bentuk jari tangan Anda secara *real-time*:

| Gesture | Posisi Jari | Fungsi |
|:---:|:---:|:---|
| ☝️ **DRAW** | **1 Jari Telunjuk** tegak lurus ke atas | **Menggambar goresan di udara** pada mode `DRW`, atau **menghapus** pada mode `ERS`. |
| ✌️ **SELECT / HOVER** | **2 Jari** (Telunjuk + Jari Tengah terbuka tegak) | **Mode Navigasi Menu / Kursor Bebas**. Arahkan ujung jari ke tombol menu atau palet warna di samping layar. Tahan selama ~0.5 detik (*dwell click*) untuk memilih tombol/warna tanpa mencoret layar. |
| 🤏 **PINCH / MOVE** | Ujung **Jempol dan Telunjuk** saling bersentuhan | **Memegang & Menggeser Objek** pada mode `MOV`. Anda juga dapat menggunakan pinch untuk mengklik tombol secara cepat. |
| 🖐️ **PALM** | **5 Jari Terbuka** (Telapak Tangan Terbuka) | **Posisi Netral**. Menghentikan coretan sementara waktu saat berpindah posisi tangan. |
| ✊ **FIST** | **Semua Jari Mengepal** | Menghentikan aksi seketika. |

---

### 3. Memilih Warna & Ketebalan (Left Toolbar)

Di sebelah kiri layar terdapat panel warna dan kuas:
- **16 Lingkaran Warna Preset**: Arahkan kursor 2 jari (✌️) ke salah satu lingkaran warna (Merah, Emas, Cyan, Hijau, dsb) untuk langsung mengubah warna kuas.
- **Rainbow Hue Slider (Slider Vertikal)**: Arahkan kursor dan geser ke atas/bawah pada bar pelangi untuk memilih warna kustom sesuai selera.
- **Preview Kuas (Pojok Kiri Bawah)**: Lingkaran di pojok kiri bawah memperlihatkan warna aktif dan ukuran kuas saat ini.

---

### 4. Menggunakan Fitur & Efek (Right Toolbar)

Di sebelah kanan layar terdapat tombol menu fungsi interaktif:

| Tombol | Nama Mode | Cara Kerja & Penjelasan |
|:---|:---|:---|
| **`DRW`** | **Draw Mode** | Mode standar untuk menggambar bebas menggunakan 1 jari telunjuk (☝️). |
| **`ERS`** | **Eraser Mode** | Lingkaran penghapus akan muncul di ujung jari telunjuk Anda. Sapukan ke garis yang ingin dihapus. |
| **`MOV`** | **Move Mode** | Mode seleksi objek. Dekatkan jari ke coretan yang telah dibuat, lalu lakukan gestur **Pinch** (🤏) untuk mengangkat dan memindahkan gambar ke area lain. |
| **`-` / `+`** | **Brush Size** | Sentuh tombol `-` untuk memperkecil diameter kuas atau `+` untuk mempertebal kuas. |
| **`GLOW`** | **Neon Glow** | Mengaktifkan efek pendaran cahaya neon estetik pada goresan gambar Anda. |
| **`MRR`** | **Mirror Symmetry** | Setiap goresan di sisi kiri akan otomatis dicerminkan di sisi kanan secara simetris. |
| **`FLL`** | **Dark Blackboard** | Menutup tampilan video kamera dan menggantinya dengan kanvas papan tulis gelap pekat. |
| **`RNBW`** | **Rainbow Brush** | Warna garis akan berubah-ubah warna pelangi secara dinamis seiring pergerakan tangan Anda. |
| **`UNDO`** | **Undo Stroke** | Menghapus goresan terakhir yang baru saja digambar. |
| **`CLEAR`**| **Clear Canvas** | Mengosongkan seluruh kanvas layar seketika. |
| **`SAVE`** | **Save Image** | Menyimpan gambar karya Anda ke dalam folder `saved/` dengan nama otomatis berdasar tanggal & jam (`canvas_YYYYMMDD_HHMMSS.png`). |

---

## ⌨️ Pintasan Keyboard (Hotkeys)

Selain menggunakan gerakan tangan, Anda juga dapat mengontrol aplikasi dengan keyboard:

| Tombol Keyboard | Fungsi |
|:---:|:---|
| <kbd>D</kbd> | Aktifkan **Draw Mode** |
| <kbd>E</kbd> | Aktifkan **Erase Mode** |
| <kbd>M</kbd> | Aktifkan **Move Mode** |
| <kbd>G</kbd> | Toggle efek **Neon Glow** (On / Off) |
| <kbd>R</kbd> | Toggle efek **Rainbow Brush** (On / Off) |
| <kbd>X</kbd> | Toggle mode **Mirror Symmetry** (On / Off) |
| <kbd>F</kbd> | Toggle layar **Dark Canvas** (On / Off) |
| <kbd>+</kbd> / <kbd>=</kbd> | Perbesar ukuran kuas |
| <kbd>-</kbd> / <kbd>_</kbd> | Perkecil ukuran kuas |
| <kbd>Z</kbd> atau <kbd>U</kbd> | **Undo** goresan terakhir |
| <kbd>C</kbd> | **Clear** seluruh kanvas |
| <kbd>S</kbd> | **Save** gambar ke folder `saved/` |
| <kbd>Q</kbd> atau <kbd>ESC</kbd> | Keluar dari aplikasi |

> 💡 **Tip Klik Mouse**: Anda juga bisa menggunakan klik kiri mouse di layar jika sedang tidak ingin menggunakan sensor tangan.

---

## 🌐 Versi Web Browser

Aplikasi ini juga dilengkapi versi web berbasis HTML5 & JavaScript yang bisa dijalankan langsung di browser:
1. Masuk ke folder `web/`.
2. Klik ganda file `index.html` (buka dengan Google Chrome atau Microsoft Edge).
3. Berikan izin akses kamera (*Allow Camera*).
4. Nikmati fitur menggambar dengan gesture tangan langsung di browser tanpa perlu setup Python!

---

## 📁 Struktur Folder

```plaintext
GestureCanvas/
├── hand_landmarker.task   # Model AI MediaPipe Hand Landmark
├── hand_tracker.py        # Modul pelacak sendi tangan & logika gesture
├── canvas.py              # Modul core engine kanvas & rendering
├── main.py                # Aplikasi utama (UI, toolbar, loop kamera)
├── requirements.txt       # Daftar dependensi Python
├── run.bat                # Skrip peluncur otomatis 1-klik di Windows
├── saved/                 # Tempat penyimpanan hasil gambar (.png)
├── web/                   # Versi web standalone
│   └── index.html         # Web app GestureCanvas berbasis browser
└── README.md              # Dokumentasi & panduan penggunaan
```

---

## ❓ Troubleshooting / FAQ

<details>
<summary><b>1. Kamera tidak terbuka / Error "Camera not detected"</b></summary>

- Pastikan webcam tidak sedang digunakan oleh aplikasi lain (seperti Zoom, Google Meet, OBS, atau browser).
- Jika Anda memiliki lebih dari satu kamera (misal: kamera internal laptop dan webcam USB), ubah indeks kamera di [main.py](file:///c:/coding/GestureCanvas/main.py):
  ```python
  app = GestureCanvasApp(camera_id=0) # ganti 0 menjadi 1 atau 2
  ```
</details>

<details>
<summary><b>2. Gerakan kursor terasa tersendat (Lag / Low FPS)</b></summary>

- Pastikan pencahayaan ruangan cukup terang. Ruangan yang gelap membuat kamera menurunkan *shutter speed* sehingga FPS berkurang.
- Kurangi beban komputasi background dengan menutup aplikasi berat lainnya.
</details>

<details>
<summary><b>3. Goresan sering terputus saat menggambar</b></summary>

- Pastikan hanya **1 jari telunjuk** yang tegak saat menggambar. Jika jari tengah ikut terangkat, sistem akan beralih ke mode seleksi (*peace sign*).
- Jaga jarak tangan agar tetap berada di area sorotan kamera.
</details>

---

## 🤝 Kontribusi & Lisensi

Dibuat dengan ❤️ untuk eksplorasi *Computer Vision & Human-Computer Interaction*.  
Silakan *fork*, beri *star* ⭐ pada repositori ini, dan kembangkan fitur baru!
