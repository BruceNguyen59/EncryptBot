from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def get_key() -> bytes:
    """Tạo key mới nếu chưa có, hoặc load key cũ"""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        print("[+] Đã tạo key mới!")
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_data(data: bytes) -> bytes:
    """Mã hóa dữ liệu"""
    return Fernet(get_key()).encrypt(data)

def decrypt_data(data: bytes) -> bytes:
    """Giải mã dữ liệu"""
    try:
        return Fernet(get_key()).decrypt(data)
    except Exception:
        raise ValueError("❌ Sai key hoặc file không hợp lệ!")