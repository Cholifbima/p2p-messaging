import customtkinter as ctk
from tkinter import messagebox
import threading
import logging
from datetime import datetime
from typing import Optional

from p2p_messaging import Peer

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.result = None
        
        self.title("Pesan P2P - Login")
        self.geometry("400x450")
        self.resizable(True, True)
        self.minsize(350, 400)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (450 // 2)
        self.geometry(f"400x450+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _create_widgets(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Selamat Datang di Pesan P2P",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Pesan Peer-to-Peer",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle.pack()
        
        form_frame = ctk.CTkFrame(container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, pady=10)
        
        name_label = ctk.CTkLabel(
            form_frame,
            text="Nama Anda",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        name_label.pack(anchor="w")
        
        self.name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Masukkan nama Anda...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.name_entry.pack(fill="x", pady=(5, 15))
        
        port_label = ctk.CTkLabel(
            form_frame,
            text="Nomor Port",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        port_label.pack(anchor="w", pady=(10, 5))
        
        self.port_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Masukkan port (default: 5000)",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.port_entry.pack(fill="x", pady=(0, 20))
        self.port_entry.insert(0, "5000")
        
        self.start_btn = ctk.CTkButton(
            form_frame,
            text="Mulai Pesan",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._on_start
        )
        self.start_btn.pack(fill="x")
        
        self.name_entry.bind("<Return>", lambda e: self._on_start())
        self.port_entry.bind("<Return>", lambda e: self._on_start())
    
    def _on_start(self):
        name = self.name_entry.get().strip()
        port_str = self.port_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Harap masukkan nama Anda!")
            return
        
        try:
            port = int(port_str) if port_str else 5000
        except ValueError:
            messagebox.showerror("Error", "Nomor port tidak valid!")
            return
        
        self.result = {"name": name, "port": port}
        self.callback(self.result)
        self.destroy()
    
    def _on_cancel(self):
        self.callback(None)
        self.destroy()


class ConnectDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        
        self.title("Hubungkan ke Peer")
        self.geometry("400x300")
        self.resizable(True, True)
        self.minsize(350, 250)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"400x300+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="🔗 Hubungkan ke Peer",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(0, 15))
        
        ip_frame = ctk.CTkFrame(container, fg_color="transparent")
        ip_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(ip_frame, text="Alamat IP:", width=80, anchor="w").pack(side="left")
        self.ip_entry = ctk.CTkEntry(ip_frame, placeholder_text="192.168.43.60")
        self.ip_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.ip_entry.insert(0, "192.168.43.60")
        
        port_frame = ctk.CTkFrame(container, fg_color="transparent")
        port_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(port_frame, text="Port:", width=80, anchor="w").pack(side="left")
        self.port_entry = ctk.CTkEntry(port_frame, placeholder_text="5000")
        self.port_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="Batal",
            width=100,
            fg_color="gray",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="Hubungkan",
            width=100,
            command=self._on_connect
        ).pack(side="right")
        
        self.ip_entry.focus()
    
    def _on_connect(self):
        ip = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Harap masukkan alamat IP!")
            return
        
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Nomor port tidak valid!")
            return
        
        self.callback(ip, port)
        self.destroy()


class MessageBubble(ctk.CTkFrame):
    def __init__(self, parent, sender: str, message: str, timestamp: str, is_own: bool = False, is_system: bool = False):
        super().__init__(parent, fg_color="transparent")
        
        self.pack(fill="x", padx=10, pady=3)
        
        if is_system:
            sys_label = ctk.CTkLabel(
                self,
                text=f"── {message} ──",
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color="#888888"
            )
            sys_label.pack(pady=5)
        else:
            bubble_frame = ctk.CTkFrame(self)
            
            if is_own:
                bubble_frame.configure(fg_color="#1f6aa5")
                bubble_frame.pack(anchor="e", padx=(50, 0))
            else:
                bubble_frame.configure(fg_color="#2b2b2b")
                bubble_frame.pack(anchor="w", padx=(0, 50))
            
            if not is_own:
                sender_label = ctk.CTkLabel(
                    bubble_frame,
                    text=sender,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#4da6ff"
                )
                sender_label.pack(anchor="w", padx=12, pady=(8, 0))
            
            msg_label = ctk.CTkLabel(
                bubble_frame,
                text=message,
                font=ctk.CTkFont(size=13),
                wraplength=300,
                justify="left"
            )
            msg_label.pack(anchor="w", padx=12, pady=(4 if not is_own else 10, 4))
            
            time_label = ctk.CTkLabel(
                bubble_frame,
                text=timestamp,
                font=ctk.CTkFont(size=9),
                text_color="#888888"
            )
            time_label.pack(anchor="e", padx=12, pady=(0, 6))


class P2PMessengerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.peer: Optional[Peer] = None
        self.is_connected = False
        self.active_peer_id = None
        self.chat_history = {}  # peer_id: list of messages
        
        self.title("Pesan P2P")
        self.geometry("900x600")
        self.resizable(True, True)
        self.minsize(700, 450)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"900x600+{x}+{y}")
        
        self._create_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._show_login)
    
    def _create_layout(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        self._create_sidebar()
        
        self.content = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content.pack(side="right", fill="both", expand=True)
        
        self._create_content()
    
    def _create_sidebar(self):
        header = ctk.CTkFrame(self.sidebar, height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        self.user_label = ctk.CTkLabel(
            header,
            text="👤 Tidak Terhubung",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.user_label.pack(side="left", padx=15, pady=15)
        
        self.status_indicator = ctk.CTkLabel(
            header,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_indicator.pack(side="right", padx=15)
        
        self.connect_btn = ctk.CTkButton(
            self.sidebar,
            text="+ Hubungkan ke Peer",
            height=35,
            command=self._show_connect_dialog
        )
        self.connect_btn.pack(fill="x", padx=10, pady=10)
        
        peers_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        peers_header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            peers_header,
            text="Peer Terhubung",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        ).pack(side="left")
        
        self.peers_count = ctk.CTkLabel(
            peers_header,
            text="(0)",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.peers_count.pack(side="right")
        
        self.peers_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.peers_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        info_frame = ctk.CTkFrame(self.sidebar, height=80)
        info_frame.pack(fill="x", side="bottom")
        info_frame.pack_propagate(False)
        
        self.ip_label = ctk.CTkLabel(
            info_frame,
            text="IP: -",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.ip_label.pack(anchor="w", padx=15, pady=(10, 2))
        
        self.port_label = ctk.CTkLabel(
            info_frame,
            text="Port: -",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.port_label.pack(anchor="w", padx=15, pady=2)
    
    def _create_content(self):
        chat_header = ctk.CTkFrame(self.content, height=50, corner_radius=0)
        chat_header.pack(fill="x")
        chat_header.pack_propagate(False)
        
        self.chat_title = ctk.CTkLabel(
            chat_header,
            text="💬 Pilih peer untuk mulai chat",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.chat_title.pack(side="left", padx=20, pady=10)
        
        self.chat_frame = ctk.CTkScrollableFrame(self.content)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.welcome_label = ctk.CTkLabel(
            self.chat_frame,
            text="👋 Selamat Datang di Pesan P2P!\n\nHubungkan ke peer lain untuk mulai chatting.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.welcome_label.pack(expand=True, pady=50)
        
        input_frame = ctk.CTkFrame(self.content, height=60, corner_radius=0)
        input_frame.pack(fill="x", side="bottom")
        input_frame.pack_propagate(False)
        
        self.msg_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ketik pesan Anda...",
            font=ctk.CTkFont(size=13)
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        self.msg_entry.bind("<Return>", lambda e: self._send_message())
        
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Kirim",
            width=80,
            command=self._send_message
        )
        self.send_btn.pack(side="right", padx=(5, 10), pady=10)
        self.send_btn.configure(state="disabled")
    
    def _show_login(self):
        self.withdraw()
        LoginWindow(self, self._on_login_complete)
    
    def _on_login_complete(self, result):
        if result is None:
            self.destroy()
            return
        
        self.peer = Peer(
            name=result["name"],
            port=result["port"],
            on_message=self._on_message_received,
            on_peer_join=self._on_peer_join,
            on_peer_leave=self._on_peer_leave
        )
        
        try:
            self.peer.start()
            self.is_connected = True
            
            self.user_label.configure(text=f"👤 {result['name']}")
            self.status_indicator.configure(text_color="#00ff00")
            self.ip_label.configure(text=f"IP: {self.peer.local_ip}")
            self.port_label.configure(text=f"Port: {result['port']}")
            
            # Enable send button
            self.send_btn.configure(state="normal")
            
            self.deiconify()
            
            self._add_system_message(f"Anda sekarang online sebagai {result['name']}")
            self._add_system_message(f"Alamat Anda: {self.peer.local_ip}:{result['port']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai peer: {e}")
            self.destroy()
    
    def _show_connect_dialog(self):
        if not self.peer:
            return
        ConnectDialog(self, self._on_connect_peer)
    
    def _on_connect_peer(self, ip: str, port: int):
        if self.peer.connect_to_peer(ip, port):
            self._add_system_message(f"Menghubungkan ke {ip}:{port}...")
        else:
            messagebox.showerror("Error", f"Gagal terhubung ke {ip}:{port}")
    
    def _send_message(self):
        if not self.peer or not self.active_peer_id:
            return
        
        message = self.msg_entry.get().strip()
        if not message:
            return
        
        # Send to specific peer
        self.peer.send_message(message, target_peer_id=self.active_peer_id)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        # Store in chat history
        if self.active_peer_id not in self.chat_history:
            self.chat_history[self.active_peer_id] = []
        
        self.chat_history[self.active_peer_id].append({
            "sender": "Anda",
            "text": message,
            "timestamp": timestamp,
            "is_own": True
        })
        
        # Refresh display
        self._refresh_chat_display()
        
        self.msg_entry.delete(0, "end")
    
    def _add_message_bubble(self, sender: str, message: str, timestamp: str, is_own: bool = False):
        if hasattr(self, 'welcome_label') and self.welcome_label.winfo_exists():
            self.welcome_label.pack_forget()
        
        MessageBubble(self.chat_frame, sender, message, timestamp, is_own)
        
        self.chat_frame._parent_canvas.yview_moveto(1.0)
    
    def _add_system_message(self, message: str):
        if hasattr(self, 'welcome_label') and self.welcome_label.winfo_exists():
            self.welcome_label.pack_forget()
        
        MessageBubble(self.chat_frame, "", message, "", is_system=True)
        self.chat_frame._parent_canvas.yview_moveto(1.0)
    
    def _select_peer(self, peer):
        self.active_peer_id = peer.peer_id
        self.chat_title.configure(text=f"💬 Chat dengan {peer.name}")
        self.send_btn.configure(state="normal")
        
        # Refresh peer list to show selection
        self._update_peers_list()
        
        # Load chat history for this peer
        self._refresh_chat_display()
    
    def _refresh_chat_display(self):
        # Clear current chat display
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        if not self.active_peer_id:
            self.welcome_label = ctk.CTkLabel(
                self.chat_frame,
                text="👋 Selamat Datang di Pesan P2P!\n\nHubungkan ke peer lain untuk mulai chatting.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            self.welcome_label.pack(expand=True, pady=50)
            return
        
        # Display chat history for active peer
        if self.active_peer_id in self.chat_history:
            for msg in self.chat_history[self.active_peer_id]:
                MessageBubble(
                    self.chat_frame,
                    msg["sender"],
                    msg["text"],
                    msg["timestamp"],
                    is_own=msg["is_own"]
                )
        
        self.chat_frame._parent_canvas.yview_moveto(1.0)
    
    def _update_peers_list(self):
        for widget in self.peers_scroll.winfo_children():
            widget.destroy()
        
        peers = self.peer.get_connected_peers() if self.peer else []
        self.peers_count.configure(text=f"({len(peers)})")
        
        for peer in peers:
            # Create clickable button for each peer
            peer_btn = ctk.CTkButton(
                self.peers_scroll,
                text=f"● {peer.name}",
                height=40,
                fg_color=("#2a2a2a" if peer.peer_id != self.active_peer_id else "#1f6aa5"),
                hover_color=("#3a3a3a" if peer.peer_id != self.active_peer_id else "#1a5490"),
                anchor="w",
                command=lambda p=peer: self._select_peer(p)
            )
            peer_btn.pack(fill="x", pady=2)
            
            # Store peer info for reference
            peer_btn.peer_info = peer
    
    def _on_message_received(self, sender_name: str, text: str, timestamp: str, sender_peer_id: str = None):
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%H:%M")
        except:
            time_str = datetime.now().strftime("%H:%M")
        
        # Store message in sender's chat history
        if sender_peer_id:
            if sender_peer_id not in self.chat_history:
                self.chat_history[sender_peer_id] = []
            
            self.chat_history[sender_peer_id].append({
                "sender": sender_name,
                "text": text,
                "timestamp": time_str,
                "is_own": False
            })
            
            # Only display if this peer is currently selected
            if sender_peer_id == self.active_peer_id:
                self.after(0, lambda: self._refresh_chat_display())
        else:
            # Fallback for system messages or unknown sender
            self.after(0, lambda: self._add_message_bubble(sender_name, text, time_str, is_own=False))
    
    def _on_peer_join(self, peer_name: str):
        self.after(0, lambda: self._add_system_message(f"🟢 {peer_name} bergabung ke jaringan"))
        self.after(0, self._update_peers_list)
    
    def _on_peer_leave(self, peer_name: str):
        self.after(0, lambda: self._add_system_message(f"🔴 {peer_name} meninggalkan jaringan"))
        self.after(0, self._update_peers_list)
    
    def _on_close(self):
        if self.peer:
            self.peer.stop()
        self.destroy()


def main():
    app = P2PMessengerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
