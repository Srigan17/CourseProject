import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from backend.app.config import settings

class AESGCMCipher:
    """
    AES-256-GCM Authenticated Encryption for sensitive healthcare records
    and serialized models stored at rest.
    Uses 12-byte cryptographically secure random nonces per encryption.
    """
    def __init__(self, key_hex: str = None):
        if key_hex:
            self.key = bytes.fromhex(key_hex)
        else:
            self.key = bytes.fromhex(settings.AES_GCM_KEY_HEX)
        if len(self.key) != 32:
            raise ValueError(f"AES-256-GCM key must be exactly 32 bytes (64 hex characters), got {len(self.key)} bytes.")
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str, associated_data: str = "health_record") -> dict:
        """
        Encrypts a string plaintext with AES-256-GCM.
        Returns base64 encoded ciphertext and nonce.
        """
        nonce = os.urandom(12)  # 96-bit recommended nonce for GCM
        ad_bytes = associated_data.encode("utf-8") if associated_data else None
        ciphertext_with_tag = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), ad_bytes)
        
        return {
            "ciphertext": base64.b64encode(ciphertext_with_tag).decode("utf-8"),
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "algorithm": "AES-256-GCM",
            "associated_data": associated_data
        }

    def decrypt(self, ciphertext_b64: str, nonce_b64: str, associated_data: str = "health_record") -> str:
        """
        Decrypts base64 encoded ciphertext and verifies authenticity tag.
        """
        nonce = base64.b64decode(nonce_b64)
        ciphertext_with_tag = base64.b64decode(ciphertext_b64)
        ad_bytes = associated_data.encode("utf-8") if associated_data else None
        plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext_with_tag, ad_bytes)
        return plaintext_bytes.decode("utf-8")

# Global singleton cipher
cipher = AESGCMCipher()
