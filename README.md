# P2P Messaging Application

Aplikasi messaging peer-to-peer dengan GUI menggunakan Python untuk Tugas Akhir Sistem Terdistribusi.

## Deskripsi

Aplikasi ini mengimplementasikan komunikasi peer-to-peer secara langsung (private messaging), di mana setiap node dapat mengirim dan menerima pesan tanpa server pusat. Setiap peer dapat melakukan chat private 1-to-1 dengan peer lain dalam jaringan.

## Arsitektur

Aplikasi ini menggunakan arsitektur **Peer-to-Peer (P2P)** yang bersifat desentralisasi:

```
    ┌──────────┐         Direct Connection         ┌──────────┐
    │  Peer A  │◄─────────────────────────────────►│  Peer B  │
    │ (Node 1) │                                   │ (Node 2) │
    └────┬─────┘                                   └────┬─────┘
         │                                              │
         │              ┌──────────┐                    │
         └─────────────►│  Peer C  │◄───────────────────┘
                        │ (Node 3) │
                        └──────────┘
```

### Komponen Utama

1. **Peer** - Node dalam jaringan P2P
2. **P2PServer** - TCP server untuk menerima koneksi incoming
3. **P2PClient** - TCP client untuk membuat koneksi ke peer lain
4. **Message** - Protokol pesan berbasis JSON
5. **GUI** - CustomTkinter interface untuk pengalaman pengguna yang modern

## Struktur Project

```
Project Akhir/
├── p2p_messaging/
│   ├── __init__.py      # Package initialization
│   ├── peer.py          # Core P2P peer implementation
│   ├── network.py       # Network/connection handling
│   ├── message.py       # Message protocol
│   └── utils.py         # Helper functions
├── main.py              # GUI Application entry point
├── requirements.txt     # Dependencies
├── README.md            # Dokumentasi ini
└── docs/
    └── REQUIREMENTS.md  # Dokumen kebutuhan sistem
```

## Instalasi

```bash
# Masuk ke direktori project
cd "Project Akhir"

# Install dependencies
pip install -r requirements.txt
```

## Cara Menjalankan

### Terminal 1 (Peer A - Alice)
```bash
python main.py
# Masukkan nama: Alice
# Masukkan port: 5000
# Klik "Mulai Pesan"
```

### Terminal 2 (Peer B - Bob)
```bash
python main.py
# Masukkan nama: Bob
# Masukkan port: 5001
# Klik "Mulai Pesan"
# Klik "+ Hubungkan ke Peer"
# Masukkan IP: 192.168.43.60
# Masukkan Port: 5000
```

### Terminal 3 (Peer C - Charlie)
```bash
python main.py
# Masukkan nama: Charlie
# Masukkan port: 5002
# Klik "Mulai Pesan"
# Hubungkan ke Alice atau Bob untuk bergabung ke jaringan
```

## Fitur GUI

### Login Window
- Input nama dan port
- Modern dark theme dengan CustomTkinter
- Window resizable untuk split-screen

### Main Application
- **Sidebar Kiri**: Daftar peer terhubung (klik untuk memilih chat)
- **Area Chat**: Tampilan percakapan private dengan peer terpilih
- **Input Pesan**: Kotak input untuk mengirim pesan
- **Connect Button**: Tambah koneksi ke peer baru

### Private Chat
- Klik nama peer di sidebar untuk memulai chat private
- Pesan hanya terlihat oleh peer yang dipilih
- Chat history disimpan per peer
- Header menampilkan "💬 Chat dengan [Nama Peer]"

## Protokol Pesan

Semua pesan menggunakan format JSON:

```json
{
  "type": "MESSAGE|BROADCAST|JOIN|LEAVE|PEERS|PING|PONG",
  "sender_id": "unique_peer_id",
  "sender_name": "username",
  "timestamp": "2024-01-01T12:00:00",
  "data": { ... },
  "target_id": "optional_target_peer_id"
}
```

### Tipe Pesan

| Type | Deskripsi |
|------|-----------|
| `JOIN` | Peer baru bergabung ke jaringan |
| `LEAVE` | Peer keluar dari jaringan |
| `MESSAGE` | Direct message ke peer tertentu |
| `BROADCAST` | Pesan ke semua peer (tidak digunakan) |
| `PEERS` | Berbagi daftar peer yang diketahui |
| `PING` | Health check |
| `PONG` | Response dari ping |

## Fitur

- **Private Chat (1-to-1)** - Kirim pesan langsung ke peer tertentu
- **GUI Modern** - CustomTkinter dengan dark theme
- **Bahasa Indonesia** - Interface lengkap Bahasa Indonesia
- **Resizable Window** - Dapat diatur untuk split-screen
- **Multi-Peer Support** - Hubungkan dengan banyak peer
- **Real-time Updates** - Notifikasi peer join/leave
- **Clean Code** - Tanpa komentar AI yang berlebihan
- **Cross-platform** - Windows, Linux, macOS

## Kebutuhan Sistem

- Python 3.7+
- customtkinter
- tkinter (biasanya included dengan Python)

## Default Configuration

- **Default IP untuk koneksi**: `192.168.43.60`
- **Default Port**: `5000`
- **Theme**: Dark Mode
- **Bahasa**: Indonesia

## Cara Penggunaan

1. **Login**: Masukkan nama dan port, klik "Mulai Pesan"
2. **Connect**: Klik "+ Hubungkan ke Peer" untuk menambah peer
3. **Chat**: Klik nama peer di sidebar, lalu ketik pesan
4. **Switch Chat**: Klik peer lain untuk beralih chat

## Teknologi

- **Language**: Python 3.12
- **GUI Framework**: CustomTkinter
- **Network**: TCP Sockets
- **Concurrency**: Threading
- **Message Protocol**: JSON

## Referensi

- M. Van Steen and A.S. Tannenbaum, Distributed System, 4th ed., distributed-system.net, 2023.
