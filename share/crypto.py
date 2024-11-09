from cryptography.fernet import Fernet
from env import crypt_key


class MyCrypt:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def crypt(self, raw: str) -> bytes:
        return self.cipher.encrypt(raw.encode())

    def decrypt(self, raw: bytes) -> str:
        return self.cipher.decrypt(raw).decode()


if __name__ == '__main__':
    cipher_key = Fernet.generate_key()
    print(cipher_key)
    mc =MyCrypt(crypt_key)
    x1 = mc.crypt('test')
    print(x1)
    x2 = x1.hex()
    print(x2)
    x3 = bytes.fromhex(x2)
    print(x3)
    x4 = mc.decrypt(x3)
    print(x4)