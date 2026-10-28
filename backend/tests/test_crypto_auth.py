import pytest
from backend.app.security.crypto import cipher
from backend.app.security.auth import hash_password, verify_password, create_access_token, decode_access_token

def test_aes_gcm_encryption_roundtrip():
    secret_text = "Patient 4671: Heart rate 84 bpm, Blood oxygen 98%"
    enc = cipher.encrypt(secret_text, associated_data="hospital_a")
    assert "ciphertext" in enc
    assert "nonce" in enc
    assert enc["ciphertext"] != secret_text

    decrypted = cipher.decrypt(enc["ciphertext"], enc["nonce"], associated_data="hospital_a")
    assert decrypted == secret_text

def test_aes_gcm_tamper_resistance():
    secret_text = "Protected vital readings"
    enc = cipher.encrypt(secret_text, associated_data="hospital_a")
    # Tampering with associated data must fail authentication
    with pytest.raises(Exception):
        cipher.decrypt(enc["ciphertext"], enc["nonce"], associated_data="attacker_altered_tag")

def test_password_hashing():
    pwd = "SecureDoctorPassword2026!"
    hashed, salt = hash_password(pwd)
    assert verify_password(pwd, hashed, salt) is True
    assert verify_password("WrongPassword", hashed, salt) is False

def test_jwt_token():
    token = create_access_token({"sub": "hospital_a", "role": "CLIENT"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.sub == "hospital_a"
    assert payload.role == "CLIENT"
