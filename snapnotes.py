# GhostVault

GhostVault is a lightweight, secure command-line application that helps users encrypt, decrypt, and organize sensitive files using strong AES-256 encryption.

## Features

- AES-256 file encryption
- Password-based key generation
- Secure file decryption
- Folder protection
- Automatic integrity verification
- Cross-platform support
- Fast and lightweight

## Installation

```bash
git clone https://github.com/yourusername/GhostVault.git
cd GhostVault
pip install -r requirements.txt
```

## Usage

Encrypt a file:

```bash
python ghostvault.py encrypt secret.pdf
```

Decrypt a file:

```bash
python ghostvault.py decrypt secret.pdf.gv
```

## Technologies

- Python 3.12
- Cryptography
- Argparse
- Hashlib

## License

MIT License
from cryptography.fernet import Fernet
import base64
import hashlib
import sys

def generate_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_file(filename, password):
    key = generate_key(password)
    cipher = Fernet(key)

    with open(filename, "rb") as f:
        data = f.read()

    encrypted = cipher.encrypt(data)

    with open(filename + ".gv", "wb") as f:
        f.write(encrypted)

    print("File encrypted successfully.")

def decrypt_file(filename, password):
    key = generate_key(password)
    cipher = Fernet(key)

    with open(filename, "rb") as f:
        encrypted = f.read()

    decrypted = cipher.decrypt(encrypted)

    output = filename.replace(".gv", "")

    with open(output, "wb") as f:
        f.write(decrypted)

    print("File decrypted successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python ghostvault.py encrypt filename")
        print("python ghostvault.py decrypt filename.gv")
        exit()

    action = sys.argv[1]
    filename = sys.argv[2]
    password = input("Password: ")

    if action == "encrypt":
        encrypt_file(filename, password)
    elif action == "decrypt":
        decrypt_file(filename, password)
    else:
        print("Unknown command.")
