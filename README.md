# P2P Messaging Application

Aplikasi messaging peer-to-peer menggunakan Python untuk Tugas Akhir Sistem Terdistribusi.

## Deskripsi

Aplikasi ini memungkinkan komunikasi langsung antar peer tanpa memerlukan server pusat. Setiap node dapat bertindak sebagai client dan server secara bersamaan.

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

## Struktur Project

```
Project Akhir/
├── p2p_messaging/
│   ├── __init__.py      # Package initialization
│   ├── peer.py          # Core P2P peer implementation
│   ├── network.py       # Network/connection handling
│   ├── message.py       # Message protocol
│   └── utils.py         # Helper functions
├── main.py              # Entry point aplikasi
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
```

### Terminal 2 (Peer B - Bob)
```bash
python main.py
# Masukkan nama: Bob
# Masukkan port: 5001
# Kemudian connect ke Alice:
/connect 127.0.0.1 5000
```

### Terminal 3 (Peer C - Charlie)
```bash
python main.py
# Masukkan nama: Charlie
# Masukkan port: 5002
# Connect ke jaringan melalui Bob:
/connect 127.0.0.1 5001
```

## Commands

| Command | Description |
|---------|-------------|
| `/connect <ip> <port>` | Connect ke peer lain |
| `/peers` | Tampilkan daftar peer yang terhubung |
| `/info` | Tampilkan informasi peer sendiri |
| `/msg <id> <text>` | Kirim direct message ke peer tertentu |
| `/help` | Tampilkan bantuan |
| `/quit` | Keluar aplikasi |
| `<text>` | Broadcast pesan ke semua peer |

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
| `BROADCAST` | Pesan ke semua peer |
| `PEERS` | Berbagi daftar peer yang diketahui |
| `PING` | Health check |
| `PONG` | Response dari ping |

## Fitur

- ✅ Koneksi peer-to-peer langsung tanpa server pusat
- ✅ Broadcast pesan ke semua peer
- ✅ Direct message ke peer tertentu
- ✅ Auto-discovery peer melalui peer list sharing
- ✅ Notifikasi join/leave
- ✅ Heartbeat untuk monitoring koneksi
- ✅ Command-line interface yang user-friendly
- ✅ Cross-platform (Windows, Linux, macOS)

## Kebutuhan Sistem

- Python 3.7+
- colorama (untuk tampilan warna di terminal)

## Referensi

- M. Van Steen and A.S. Tannenbaum, Distributed System, 4th ed., distributed-system.net, 2023.
