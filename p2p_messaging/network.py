"""
Network Layer for P2P Communication
Handles TCP connections, both server and client sides
"""
import socket
import threading
import logging
from typing import Dict, Callable, Optional, Tuple
from .message import Message

logger = logging.getLogger(__name__)


class ConnectionHandler:
    """
    Handles a single peer connection
    Manages reading/writing messages over the socket
    """
    
    def __init__(
        self,
        sock: socket.socket,
        address: Tuple[str, int],
        peer_id: Optional[str] = None,
        on_message: Optional[Callable[[Message, 'ConnectionHandler'], None]] = None,
        on_disconnect: Optional[Callable[['ConnectionHandler'], None]] = None
    ):
        self.socket = sock
        self.address = address
        self.peer_id = peer_id
        self.peer_name = None
        self.on_message = on_message
        self.on_disconnect = on_disconnect
        self.running = False
        self.receive_thread = None
        self.buffer = ""
    
    def start(self):
        """Start receiving messages in a separate thread"""
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
    
    def stop(self):
        """Stop the connection handler"""
        self.running = False
        try:
            self.socket.close()
        except:
            pass
    
    def send(self, message: Message):
        """Send a message through this connection"""
        try:
            self.socket.sendall(message.to_bytes())
        except Exception as e:
            logger.error(f"Error sending message to {self.address}: {e}")
            self._handle_disconnect()
    
    def _receive_loop(self):
        """Main loop for receiving messages"""
        self.socket.settimeout(1.0)  # Allow periodic checking of running flag
        
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self._handle_disconnect()
                    break
                
                self.buffer += data.decode('utf-8')
                
                # Process complete messages (newline-delimited)
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = Message.from_json(line)
                            if self.on_message:
                                self.on_message(message, self)
                        except Exception as e:
                            logger.error(f"Error parsing message: {e}")
                            
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Connection error with {self.address}: {e}")
                    self._handle_disconnect()
                break
    
    def _handle_disconnect(self):
        """Handle disconnection"""
        self.running = False
        if self.on_disconnect:
            self.on_disconnect(self)


class P2PServer:
    """
    TCP Server that listens for incoming peer connections
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        on_connection: Callable[[ConnectionHandler], None]
    ):
        self.host = host
        self.port = port
        self.on_connection = on_connection
        self.server_socket = None
        self.running = False
        self.accept_thread = None
    
    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.server_socket.settimeout(1.0)
        
        self.running = True
        self.accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.accept_thread.start()
        
        logger.info(f"P2P Server listening on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def _accept_loop(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"New connection from {address}")
                
                handler = ConnectionHandler(client_socket, address)
                self.on_connection(handler)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")


class P2PClient:
    """
    TCP Client for connecting to other peers
    """
    
    @staticmethod
    def connect(
        host: str,
        port: int,
        timeout: float = 5.0
    ) -> Optional[ConnectionHandler]:
        """
        Connect to a peer
        
        Args:
            host: Target host
            port: Target port
            timeout: Connection timeout
            
        Returns:
            ConnectionHandler if successful, None otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.settimeout(None)
            
            handler = ConnectionHandler(sock, (host, port))
            logger.info(f"Connected to peer at {host}:{port}")
            return handler
            
        except Exception as e:
            logger.error(f"Failed to connect to {host}:{port}: {e}")
            return None
