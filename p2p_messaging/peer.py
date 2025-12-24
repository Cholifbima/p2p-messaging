# Implementasi P2P Peer
import threading
import logging
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime

from .network import P2PServer, P2PClient, ConnectionHandler
from .message import Message, MessageType
from .utils import generate_peer_id, get_local_ip, format_peer_address

logger = logging.getLogger(__name__)


class PeerInfo:
    # Info tentang peer di jaringan
    
    def __init__(self, peer_id: str, name: str, host: str, port: int):
        self.peer_id = peer_id
        self.name = name
        self.host = host
        self.port = port
        self.last_seen = datetime.now()
    
    def to_dict(self) -> dict:
        # ubah ke format dict
        return {
            "peer_id": self.peer_id,
            "name": self.name,
            "host": self.host,
            "port": self.port
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PeerInfo':
        return cls(
            peer_id=data["peer_id"],
            name=data["name"],
            host=data["host"],
            port=data["port"]
        )
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"


class Peer:
    # Class utama untuk komunikasi P2P
    
    def __init__(
        self,
        name: str,
        port: int,
        host: str = "0.0.0.0",
        on_message: Optional[Callable[[str, str, str], None]] = None,
        on_peer_join: Optional[Callable[[str], None]] = None,
        on_peer_leave: Optional[Callable[[str], None]] = None,
        on_peer_disconnect: Optional[Callable[[str], None]] = None
    ):
        self.name = name
        self.port = port
        self.host = host
        self.peer_id = generate_peer_id(name, port)
        self.local_ip = get_local_ip()
        
        # Callbacks
        self.on_message = on_message
        self.on_peer_join = on_peer_join
        self.on_peer_leave = on_peer_leave
        
        # Network components
        self.server: Optional[P2PServer] = None
        self.connections: Dict[str, ConnectionHandler] = {}  # peer_id -> handler
        self.known_peers: Dict[str, PeerInfo] = {}  # peer_id -> PeerInfo
        
        # Thread safety
        self.lock = threading.Lock()
        
        # State
        self.running = False
        self.heartbeat_thread = None
    
    def start(self):
        # jalankan peer
        # Start server
        self.server = P2PServer(
            host=self.host,
            port=self.port,
            on_connection=self._handle_new_connection
        )
        self.server.start()
        
        self.running = True
        
        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        logger.info(f"Peer '{self.name}' started on {self.local_ip}:{self.port}")
        logger.info(f"Peer ID: {self.peer_id}")
    
    def stop(self):
        # stop peer
        self.running = False
        
        # Notify peers we're leaving
        leave_msg = Message(
            msg_type=MessageType.LEAVE,
            sender_id=self.peer_id,
            sender_name=self.name,
            data={"reason": "shutdown"}
        )
        self._broadcast_message(leave_msg)
        
        # Close all connections
        with self.lock:
            for handler in self.connections.values():
                handler.stop()
            self.connections.clear()
        
        # Stop server
        if self.server:
            self.server.stop()
        
        logger.info(f"Peer '{self.name}' stopped")
    
    def connect_to_peer(self, host: str, port: int) -> bool:
        # konek ke peer lain
        handler = P2PClient.connect(host, port)
        if not handler:
            return False
        
        # Set up message handling
        handler.on_message = self._handle_message
        handler.on_disconnect = self._handle_disconnect
        handler.start()
        
        # Send JOIN message
        join_msg = Message(
            msg_type=MessageType.JOIN,
            sender_id=self.peer_id,
            sender_name=self.name,
            data={
                "host": self.local_ip,
                "port": self.port
            }
        )
        handler.send(join_msg)
        
        return True
    
    def send_message(self, text: str, target_peer_id: Optional[str] = None):
        # kirim pesan
        if target_peer_id:
            # Direct message
            msg = Message(
                msg_type=MessageType.MESSAGE,
                sender_id=self.peer_id,
                sender_name=self.name,
                data={"text": text},
                target_id=target_peer_id
            )
            
            with self.lock:
                if target_peer_id in self.connections:
                    self.connections[target_peer_id].send(msg)
                else:
                    logger.warning(f"Peer {target_peer_id} not connected")
        else:
            # Broadcast
            msg = Message(
                msg_type=MessageType.BROADCAST,
                sender_id=self.peer_id,
                sender_name=self.name,
                data={"text": text}
            )
            self._broadcast_message(msg)
    
    def get_connected_peers(self) -> List[PeerInfo]:
        # dapetin daftar peer yang konek
        with self.lock:
            return [
                self.known_peers[pid] 
                for pid in self.connections.keys() 
                if pid in self.known_peers
            ]
    
    def get_peer_info(self) -> dict:
        # info peer ini
        return {
            "peer_id": self.peer_id,
            "name": self.name,
            "host": self.local_ip,
            "port": self.port
        }
    
    # ---- Private Methods ----
    
    def _handle_new_connection(self, handler: ConnectionHandler):
        # handle koneksi baru
        handler.on_message = self._handle_message
        handler.on_disconnect = self._handle_disconnect
        handler.start()
    
    def _handle_message(self, message: Message, handler: ConnectionHandler):
        # handle pesan masuk
        msg_type = message.msg_type
        
        if msg_type == MessageType.JOIN:
            self._handle_join(message, handler)
            
        elif msg_type == MessageType.LEAVE:
            self._handle_leave(message, handler)
            
        elif msg_type == MessageType.MESSAGE or msg_type == MessageType.BROADCAST:
            self._handle_chat_message(message)
            
        elif msg_type == MessageType.PEERS:
            self._handle_peers_list(message, handler)
            
        elif msg_type == MessageType.PING:
            self._handle_ping(message, handler)
            
        elif msg_type == MessageType.PONG:
            self._handle_pong(message)
    
    def _handle_join(self, message: Message, handler: ConnectionHandler):
        # handle JOIN message
        peer_id = message.sender_id
        peer_name = message.sender_name
        data = message.data
        
        # Create peer info
        peer_info = PeerInfo(
            peer_id=peer_id,
            name=peer_name,
            host=data["host"],
            port=data["port"]
        )
        
        # Store connection and peer info
        handler.peer_id = peer_id
        handler.peer_name = peer_name
        
        with self.lock:
            self.connections[peer_id] = handler
            self.known_peers[peer_id] = peer_info
        
        logger.info(f"Peer joined: {peer_name} ({peer_id[:8]}...)")
        
        # Send our peer list to the new peer
        peers_data = [p.to_dict() for p in self.known_peers.values() if p.peer_id != peer_id]
        peers_msg = Message(
            msg_type=MessageType.PEERS,
            sender_id=self.peer_id,
            sender_name=self.name,
            data={
                "peers": peers_data,
                "my_info": self.get_peer_info()
            }
        )
        handler.send(peers_msg)
        
        # Notify callback
        if self.on_peer_join:
            self.on_peer_join(peer_name)
    
    def _handle_leave(self, message: Message, handler: ConnectionHandler):
        # handle LEAVE message
        peer_id = message.sender_id
        peer_name = message.sender_name
        
        with self.lock:
            if peer_id in self.connections:
                del self.connections[peer_id]
            if peer_id in self.known_peers:
                del self.known_peers[peer_id]
        
        logger.info(f"Peer left: {peer_name}")
        
        if self.on_peer_leave:
            self.on_peer_leave(peer_name)
    
    def _handle_chat_message(self, message: Message):
        # handle pesan chat
        text = message.data.get("text", "")
        sender_name = message.sender_name
        sender_id = message.sender_id
        timestamp = message.timestamp
        
        if self.on_message:
            self.on_message(sender_name, text, timestamp, sender_id)
    
    def _handle_peers_list(self, message: Message, handler: ConnectionHandler):
        # handle daftar peers
        data = message.data
        
        # Store sender's info
        if "my_info" in data:
            my_info = data["my_info"]
            peer_info = PeerInfo.from_dict(my_info)
            peer_id = my_info["peer_id"]
            
            with self.lock:
                self.known_peers[peer_id] = peer_info
                # Store the handler for this peer
                handler.peer_id = peer_id
                handler.peer_name = my_info["name"]
                self.connections[peer_id] = handler
            
            # Notify that peer has joined (for the initiating peer)
            # Call outside lock to prevent deadlock
            if self.on_peer_join:
                self.on_peer_join(my_info["name"])
        
        # Connect to other known peers
        peers = data.get("peers", [])
        for peer_data in peers:
            peer_id = peer_data["peer_id"]
            if peer_id != self.peer_id and peer_id not in self.connections:
                # Try to connect to this peer
                threading.Thread(
                    target=self.connect_to_peer,
                    args=(peer_data["host"], peer_data["port"]),
                    daemon=True
                ).start()
    
    def _handle_ping(self, message: Message, handler: ConnectionHandler):
        # handle ping
        pong_msg = Message(
            msg_type=MessageType.PONG,
            sender_id=self.peer_id,
            sender_name=self.name
        )
        handler.send(pong_msg)
    
    def _handle_pong(self, message: Message):
        # handle PONG response
        peer_id = message.sender_id
        with self.lock:
            if peer_id in self.known_peers:
                self.known_peers[peer_id].last_seen = datetime.now()
    
    def _handle_disconnect(self, handler: ConnectionHandler):
        """Handle peer disconnection"""
        peer_id = handler.peer_id
        peer_name = handler.peer_name or "Unknown"
        
        with self.lock:
            if peer_id and peer_id in self.connections:
                del self.connections[peer_id]
            if peer_id and peer_id in self.known_peers:
                del self.known_peers[peer_id]
        
        logger.info(f"Peer disconnected: {peer_name}")
        
        if self.on_peer_leave and peer_name != "Unknown":
            self.on_peer_leave(peer_name)
    
    def _broadcast_message(self, message: Message):
        """Send message to all connected peers"""
        with self.lock:
            for handler in list(self.connections.values()):
                try:
                    handler.send(message)
                except:
                    pass
    
    def _heartbeat_loop(self):
        """Periodic heartbeat to check peer connections"""
        while self.running:
            time.sleep(30)  # Every 30 seconds
            
            ping_msg = Message(
                msg_type=MessageType.PING,
                sender_id=self.peer_id,
                sender_name=self.name
            )
            self._broadcast_message(ping_msg)
