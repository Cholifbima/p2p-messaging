# Protokol pesan P2P
import json
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional


class MessageType(Enum):
    # Tipe pesan P2P
    MESSAGE = "MESSAGE"          # Pesan chat biasa
    BROADCAST = "BROADCAST"      # Broadcast ke semua peer
    JOIN = "JOIN"               # Peer bergabung ke jaringan
    LEAVE = "LEAVE"             # Peer keluar dari jaringan
    PEERS = "PEERS"             # Daftar peer yang diketahui
    PING = "PING"               # Health check
    PONG = "PONG"               # Response to ping
    DISCOVERY = "DISCOVERY"     # Peer discovery request


class Message:
    # Representasi pesan P2P
    
    def __init__(
        self,
        msg_type: MessageType,
        sender_id: str,
        sender_name: str,
        data: Any = None,
        target_id: Optional[str] = None
    ):
        self.msg_type = msg_type
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.timestamp = datetime.now().isoformat()
        self.data = data
        self.target_id = target_id
    
    def to_dict(self) -> Dict[str, Any]:
        # ubah ke dict
        return {
            "type": self.msg_type.value,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "timestamp": self.timestamp,
            "data": self.data,
            "target_id": self.target_id
        }
    
    def to_json(self) -> str:
        # ubah ke JSON
        # Ubah pesan ke JSON
        return json.dumps(self.to_dict())
    
    def to_bytes(self) -> bytes:
        # ubah ke bytes
        # Ubah pesan ke bytes untuk transmisi jaringan
        return (self.to_json() + "\n").encode('utf-8')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        # buat dari dict
        # Buat pesan dari dictionary
        msg = cls(
            msg_type=MessageType(data["type"]),
            sender_id=data["sender_id"],
            sender_name=data["sender_name"],
            data=data.get("data"),
            target_id=data.get("target_id")
        )
        msg.timestamp = data.get("timestamp", msg.timestamp)
        return msg
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        # buat dari JSON
        # Buat pesan dari JSON
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        # buat dari bytes
        # Buat pesan dari bytes
        return cls.from_json(data.decode('utf-8').strip())
    
    def __str__(self) -> str:
        return f"[{self.msg_type.value}] {self.sender_name}: {self.data}"
