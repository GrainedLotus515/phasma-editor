#!/usr/bin/env python3
"""
PhasmoEditor - Python Port
A tool for editing Phasmophobia save files.

Port of stth12/PhasmoEditor from C# to Python.
Uses AES-CBC encryption with PBKDF2 key derivation.

DISCLAIMER: This tool is for educational purposes only. Use responsibly and at your own risk.
Always backup your save files before editing!

Requirements:
    pip install cryptography
"""

import os
import sys
import json
import shutil
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# The password used by Phasmophobia for AES encryption
PASSWORD = b"t36gref9u84y7f43g"


def get_save_paths() -> dict:
    """Get Phasmophobia save file paths."""
    if sys.platform == "win32":
        user_profile = os.environ.get("USERPROFILE", "")
        save_dir = Path(user_profile) / "AppData" / "LocalLow" / "Kinetic Games" / "Phasmophobia"
    elif sys.platform == "linux":
        # Steam Proton path
        save_dir = (Path.home() / ".steam" / "steam" / "steamapps" / "compatdata" / 
                   "739630" / "pfx" / "drive_c" / "users" / "steamuser" / 
                   "AppData" / "LocalLow" / "Kinetic Games" / "Phasmophobia")
    else:
        save_dir = Path.cwd()
    
    return {
        "dir": save_dir,
        "save_file": save_dir / "SaveFile.txt",
        "decrypted": save_dir / "SaveFile_Decrypted.txt",
        "encrypted": save_dir / "SaveFile_Encrypted.txt",
        "backup": save_dir / "SaveFileBackup.txt",
    }


def derive_key(password: bytes, iv: bytes) -> bytes:
    """Derive AES key using PBKDF2 (matching C# Rfc2898DeriveBytes)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=16,
        salt=iv,
        iterations=100,
        backend=default_backend()
    )
    return kdf.derive(password)


def decrypt(file_path: Path) -> str:
    """Decrypt Phasmophobia save file using AES-CBC."""
    data = file_path.read_bytes()
    
    # First 16 bytes are the IV
    iv = data[:16]
    encrypted_data = data[16:]
    
    # Derive key using PBKDF2
    key = derive_key(PASSWORD, iv)
    
    # Decrypt using AES-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Decode and strip padding (remove trailing bytes until we hit '}')
    decrypted_text = decrypted_padded.decode('utf-8', errors='ignore')
    while decrypted_text and decrypted_text[-1] != '}':
        decrypted_text = decrypted_text[:-1]
    
    return decrypted_text


def repair_json(text: str) -> str:
    """Attempt to repair common JSON issues from .NET serialization."""
    import re
    
    # Fix unquoted numeric keys like {0:39,42:4} -> {"0":39,"42":4}
    # This handles the Dictionary<int,int> serialization from C#
    def fix_numeric_keys(match):
        content = match.group(1)
        # Add quotes around numeric keys
        fixed = re.sub(r'(\{|,)(\d+):', r'\1"\2":', content)
        return fixed
    
    # Find all {...} blocks and fix numeric keys in them
    # We need to be careful to only fix dictionary-style objects
    text = re.sub(r'(\{[0-9:,\s]+\})', fix_numeric_keys, text)
    
    # Also handle cases where it's part of a larger structure
    # Fix pattern like: "value" : {0:39,42:4,12:1}
    text = re.sub(r'(\{)(\d+):', r'\1"\2":', text)
    text = re.sub(r',(\d+):', r',"\1":', text)
    
    # Fix trailing commas before } or ]
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    return text


def encrypt(data: str) -> bytes:
    """Encrypt data for Phasmophobia save file using AES-CBC."""
    # Normalize JSON formatting
    data = data.replace("'", '"').replace("True", "true").replace("False", "false")
    
    # Generate random IV
    iv = os.urandom(16)
    
    # Derive key using PBKDF2
    key = derive_key(PASSWORD, iv)
    
    # Pad data to AES block size (16 bytes) using PKCS7
    data_bytes = data.encode('utf-8')
    padding_length = 16 - (len(data_bytes) % 16)
    padded_data = data_bytes + bytes([padding_length] * padding_length)
    
    # Encrypt using AES-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Prepend IV to encrypted data
    return iv + encrypted_data


def update_field(json_obj: dict, field_name: str) -> bool:
    """Update a field in the JSON object interactively."""
    if field_name in json_obj and json_obj[field_name] is not None:
        current_value = json_obj[field_name].get("value", "N/A")
        print(f"\nCurrent {field_name}: {current_value}")
        print(f"Enter a new value for {field_name} (or press Enter to skip):")
        
        user_input = input().strip()
        if user_input:
            try:
                new_value = int(user_input)
                json_obj[field_name]["value"] = new_value
                print("The value has been successfully updated!")
                return True
            except ValueError:
                print("Incorrect input. Please enter an integer.")
        return False
    else:
        print(f"The {field_name} wasn't found in the file.")
        return False


def main():
    """Main entry point - mirrors the original C# program flow."""
    paths = get_save_paths()
    
    print("       PhasmoEditor by stth12")
    print("        (Python Port)")
    print(" ----------------------------------")
    print("              Github")
    print("    https://github.com/stth12")
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Check if save file exists
    if not paths["save_file"].exists():
        print(f"The Phasmophobia SaveFile doesn't exist: '{paths['save_file']}'")
        input("Press any key to exit . . .")
        sys.exit(0)
    
    # Create backup
    if paths["backup"].exists():
        paths["backup"].unlink()
    shutil.copy(paths["save_file"], paths["backup"])
    print(f"Backup created: {paths['backup']}")
    
    # Delete old decrypted file if exists
    if paths["decrypted"].exists():
        paths["decrypted"].unlink()
    
    # Decrypt save file
    print("Decrypting save file...")
    try:
        decrypted_text = decrypt(paths["save_file"])
        paths["decrypted"].write_text(decrypted_text, encoding='utf-8')
        print("Decryption successful!")
    except Exception as e:
        print(f"Error decrypting file: {e}")
        input("Press any key to exit . . .")
        sys.exit(1)
    
    # Parse JSON
    try:
        json_obj = json.loads(decrypted_text)
    except json.JSONDecodeError as e:
        print(f"Initial JSON parse failed: {e}")
        print("Attempting to repair JSON...")
        
        # Try to repair the JSON
        repaired_text = repair_json(decrypted_text)
        paths["decrypted"].write_text(repaired_text, encoding='utf-8')
        
        try:
            json_obj = json.loads(repaired_text)
            print("JSON repair successful!")
            decrypted_text = repaired_text
        except json.JSONDecodeError as e2:
            print(f"JSON repair failed: {e2}")
            print(f"\nThe decrypted file has been saved to: {paths['decrypted']}")
            print("You can manually inspect and fix it.")
            
            # Show the problematic area
            error_pos = e2.pos
            start = max(0, error_pos - 50)
            end = min(len(repaired_text), error_pos + 50)
            print(f"\nProblematic area around position {error_pos}:")
            print(f"...{repaired_text[start:end]}...")
            
            input("Press any key to exit . . .")
            sys.exit(1)
    
    # Update fields
    update_field(json_obj, "PlayersMoney")
    update_field(json_obj, "NewLevel")
    update_field(json_obj, "Prestige")
    
    # Save updated JSON
    updated_content = json.dumps(json_obj, separators=(',', ':'))
    paths["decrypted"].write_text(updated_content, encoding='utf-8')
    
    # Encrypt and save
    print("\nEncrypting save file...")
    encrypted_data = encrypt(updated_content)
    paths["encrypted"].write_bytes(encrypted_data)
    print("Encryption successful!")
    
    # Create final backup and replace save file
    if paths["backup"].exists():
        paths["backup"].unlink()
    shutil.copy(paths["save_file"], paths["backup"])
    
    paths["save_file"].unlink()
    paths["decrypted"].unlink()
    
    shutil.move(str(paths["encrypted"]), str(paths["save_file"]))
    
    print()
    print("Thanx for using PhasmoEditor by stth12.")
    print("       (Python Port)")
    print("---------------------------------------")
    print("              Github")
    print("     https://github.com/stth12")
    print()
    print("          DonationAlerts")
    print("https://www.donationalerts.com/r/stth12")
    print()
    input("         Press any key...")


if __name__ == "__main__":
    main()
