# GestureCanvas - AI Hand Gesture Air Canvas

Program ini mereplikasi secara presisi aplikasi **GestureCanvas** dari video viral TikTok [@stylegwn.css](https://vt.tiktok.com/ZSqpv96Nk/). Program ini memungkinkan Anda menggambar di udara (*Air Drawing*) menggunakan kamera webcam dengan pelacakan sendi tangan real-time berbasis **Python**, **OpenCV**, dan **Google MediaPipe**.

---

## Fitur Utama

- **Real-Time Hand Tracking**: Melacak 21 landmark sendi tangan dengan skeleton kawat perak futuristik (*cyberpunk wireframe*).
- **Left Toolbar (Palet Warna & Slider)**:
  - 16 lingkaran warna preset (Gold, Orange, Red, Pink, Purple, Teal, Lime Green, White, Silver, Black, dll).
  - Indikator ring seleksi aktif.
  - **Rainbow Hue Spectrum Slider** vertikal untuk memilih warna kustom.
  - Lingkaran preview warna dan ketebalan kuas aktif di pojok kiri bawah.
- **Right Toolbar (Kontrol & Efek)**:
  - `DRW` (Draw Mode): Menggambar garis bebas di udara.
  - `ERS` (Erase Mode): Menghapus goresan gambar di dekat kursor jari.
  - `MOV` (Move Mode): Memilih dan menggeser/mentranslasikan objek coretan gambar (seperti memindahkan mahkota atau rokok pada video TikTok).
  - `-` / `+`: Mengurangi dan menambah ketebalan kuas secara interaktif.
  - `GLOW`: Efek lampu neon bercahaya (*multi-scale bloom glow*).
  - `MRR` (Mirror): Mode simetri bilateral (menggambar di kedua sisi layar secara bersamaan).
  - `FLL` (Dark Blackboard): Mengubah background menjadi kanvas papan tulis gelap.
  - `RNBW` (Rainbow Brush): Kuas pelangi yang warnanya berganti secara dinamis saat menggores.
  - `UNDO (count)`: Membatalkan goresan sebelumnya dengan indikator jumlah tersisa.
  - `CLEAR`: Membersihkan seluruh kanvas.
  - `SAVE`: Menyimpan hasil karya beresolusi tinggi ke folder `saved/` dalam format `.png`.
- **Dukungan Dual-Input**: Dapat dikontrol penuh menggunakan **gerakan tangan di depan kamera**, maupun menggunakan **mouse / klik**.
- **Versi Web Standalone (`web/index.html`)**: Versi browser interaktif yang bisa langsung dibuka di Chrome atau Edge tanpa terminal.

---

## Panduan Gesture Tangan

| Gesture | Posisi Jari | Fungsi |
|---|---|---|
| **DRAW** | Hanya **1 Jari Telunjuk** tegak lurus | Menggambar goresan garis di udara (*DRW mode*) atau menghapus (*ERS mode*) |
| **SELECT / HOVER** | **2 Jari** tegak (Telunjuk + Tengah) | Mengarahkan kursor ke menu/tombol/warna tanpa menggambar (*peace sign*) |
| **PINCH / MOVE** | Ujung **Jempol & Telunjuk** bersentuhan | Memegang dan menggeser gambar di layar (*MOV mode*), atau klik tombol |
| **PALM** | Seluruh 5 jari terbuka | Posisi netral / berhenti menggambar |
| **FIST** | Seluruh jari mengepal | Berhenti seketika |

---

## Cara Menjalankan

### Cara 1: Menggunakan File Batch (Windows - Paling Mudah)
Cukup klik ganda file:
```
run.bat
```

### Cara 2: Melalui Terminal / Command Prompt
1. Buka folder proyek:
   ```bash
   cd C:\Users\razor\.gemini\antigravity\scratch\GestureCanvas
   ```
2. Pastikan dependensi terpasang:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan program utama:
   ```bash
   python main.py
   ```

### Cara 3: Menggunakan Browser Web (Langsung Klik)
Buka file berikut di Google Chrome atau Microsoft Edge:
```
C:\Users\razor\.gemini\antigravity\scratch\GestureCanvas\web\index.html
```

---

## Tombol Pintasan Keyboard (Hotkeys)

- `D`: Beralih ke **Draw Mode**
- `E`: Beralih ke **Erase Mode**
- `M`: Beralih ke **Move Mode**
- `G`: Aktifkan / Nonaktifkan **Neon Glow**
- `R`: Aktifkan / Nonaktifkan **Rainbow Brush**
- `X`: Aktifkan / Nonaktifkan **Mirror Symmetry**
- `F`: Aktifkan / Nonaktifkan **Dark Canvas**
- `Z` atau `U`: **Undo** goresan terakhir
- `C`: **Clear** / Bersihkan seluruh kanvas
- `S`: **Save** / Simpan gambar ke folder `saved/`
- `+` / `-`: Perbesar / perkecil ukuran kuas
- `Q` atau `ESC`: Keluar dari aplikasi
