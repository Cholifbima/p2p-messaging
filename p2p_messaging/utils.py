"""
Utility functions for P2P Messaging
"""
import socket
import uuid
import hashlib
from typing import Optional


def get_local_ip() -> str:
    """Get the local IP address of this machine"""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"


def generate_peer_id(name: str, port: int) -> str:
    """
    Generate a unique peer ID based on name and port
    
    Args:
        name: Peer name
        port: Listening port
        
    Returns:
        Unique peer ID string
    """
    unique_str = f"{name}:{port}:{uuid.uuid4().hex[:8]}"
    return hashlib.sha256(unique_str.encode()).hexdigest()[:16]


def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """Check if a port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.close()
        return True
    except:
        return False


def find_available_port(start_port: int = 5000, end_port: int = 6000) -> Optional[int]:
    """Find an available port in the given range"""
    for port in range(start_port, end_port):
        if is_port_available(port):
            return port
    return None


def format_peer_address(host: str, port: int) -> str:
    """Format peer address as string"""
    return f"{host}:{port}"


def parse_peer_address(address: str) -> tuple:
    """Parse peer address string to (host, port)"""
    parts = address.split(":")
    return parts[0], int(parts[1])
