
print(60*"=")

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib
import os


class Master:
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        self.shared_key = None  # ✅ store derived 128-bit key
        self.secoc_key = None

    def get_public_bytes(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def derive_shared_key(self, peer_public_bytes):
        peer_public_key = serialization.load_pem_public_key(peer_public_bytes)
        shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)

        # 128-bit key
        self.shared_key = hashlib.sha256(shared_secret).digest()[:16]
        return self.shared_key

    def generate_secoc_key(self):
        # AES-128 key (16 bytes)
        self.secoc_key = os.urandom(16)
        return self.secoc_key
    
    def get_secoc_key(self):
        return self.secoc_key

    def encrypt_secoc_key(self, secoc_key):
        if self.shared_key is None:
            raise ValueError("Shared key not established")

        iv = os.urandom(16)

        # AES-CBC encryption
        cipher = Cipher(algorithms.AES(self.shared_key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        # PKCS7 padding (AES block = 16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(secoc_key) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return iv, ciphertext


class Anchor:
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        self.shared_key = None  # ✅ store derived 128-bit key
        self.secoc_key = None

    def get_public_bytes(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def derive_shared_key(self, peer_public_bytes):
        peer_public_key = serialization.load_pem_public_key(peer_public_bytes)
        shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)

        self.shared_key = hashlib.sha256(shared_secret).digest()[:16]
        return self.shared_key

    def decrypt_secoc_key(self, iv, ciphertext):
        if self.shared_key is None:
            raise ValueError("Shared key not established")

        cipher = Cipher(algorithms.AES(self.shared_key), modes.CBC(iv))
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        self.secoc_key = unpadder.update(padded_data) + unpadder.finalize()

        return self.secoc_key
    
    def get_secoc_key(self):
        return self.secoc_key


# --- Simulation ---

master = Master()
anchor = Anchor()

# Exchange public keys
master_pub = master.get_public_bytes()
anchor_pub = anchor.get_public_bytes()

# Derive shared key (stored internally)
master.derive_shared_key(anchor_pub)
anchor.derive_shared_key(master_pub)

print(master.shared_key == anchor.shared_key)  # ✅ True

# Master generates SecOC key
secoc_key = master.generate_secoc_key()

# Master encrypts it
iv, encrypted_key = master.encrypt_secoc_key(secoc_key)

# Anchor decrypts it
decrypted_key = anchor.decrypt_secoc_key(iv, encrypted_key)

print(secoc_key == decrypted_key)  # ✅ True
print(master.get_secoc_key())
print(anchor.get_secoc_key())