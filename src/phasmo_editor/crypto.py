"""
Cryptography module for Phasmophobia save files.

Handles AES-CBC encryption/decryption with PBKDF2 key derivation,
matching the C# implementation used by the game.
"""

import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# The password used by Phasmophobia for AES encryption
PASSWORD = b"t36gref9u84y7f43g"


def derive_key(password: bytes, iv: bytes) -> bytes:
    """
    Derive AES key using PBKDF2 (matching C# Rfc2898DeriveBytes).

    Args:
        password: The encryption password
        iv: The initialization vector (used as salt)

    Returns:
        16-byte AES key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=16,
        salt=iv,
        iterations=100,
        backend=default_backend(),
    )
    return kdf.derive(password)


def decrypt(data: bytes) -> str:
    """
    Decrypt Phasmophobia save file data using AES-CBC.

    Args:
        data: Raw encrypted bytes from save file

    Returns:
        Decrypted JSON string

    Raises:
        ValueError: If decryption fails
    """
    if len(data) < 16:
        raise ValueError("Data too short - must contain at least 16 bytes for IV")

    # First 16 bytes are the IV
    iv = data[:16]
    encrypted_data = data[16:]

    # Derive key using PBKDF2
    key = derive_key(PASSWORD, iv)

    # Decrypt using AES-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    # Decode and strip PKCS7 padding (remove trailing bytes until we hit '}')
    decrypted_text = decrypted_padded.decode("utf-8", errors="ignore")
    while decrypted_text and decrypted_text[-1] != "}":
        decrypted_text = decrypted_text[:-1]

    return decrypted_text


def decrypt_file(file_path: Path) -> str:
    """
    Decrypt a Phasmophobia save file.

    Args:
        file_path: Path to the encrypted save file

    Returns:
        Decrypted JSON string
    """
    data = file_path.read_bytes()
    return decrypt(data)


def encrypt(data: str) -> bytes:
    """
    Encrypt data for Phasmophobia save file using AES-CBC.

    Args:
        data: JSON string to encrypt

    Returns:
        Encrypted bytes (IV + ciphertext)
    """
    # Normalize JSON formatting for game compatibility
    data = data.replace("'", '"').replace("True", "true").replace("False", "false")

    # Generate random IV
    iv = os.urandom(16)

    # Derive key using PBKDF2
    key = derive_key(PASSWORD, iv)

    # Pad data to AES block size (16 bytes) using PKCS7
    data_bytes = data.encode("utf-8")
    padding_length = 16 - (len(data_bytes) % 16)
    padded_data = data_bytes + bytes([padding_length] * padding_length)

    # Encrypt using AES-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Prepend IV to encrypted data
    return iv + encrypted_data


def encrypt_to_file(data: str, file_path: Path) -> None:
    """
    Encrypt data and write to a file.

    Args:
        data: JSON string to encrypt
        file_path: Path to write encrypted data
    """
    encrypted = encrypt(data)
    file_path.write_bytes(encrypted)
