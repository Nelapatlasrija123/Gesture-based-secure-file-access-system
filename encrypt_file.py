from cryptography.fernet import Fernet

# generate encryption key
key = Fernet.generate_key()

# save key
with open("key.key", "wb") as key_file:
    key_file.write(key)

fernet = Fernet(key)

# read original file
with open("secret.txt", "rb") as file:
    data = file.read()

# encrypt file
encrypted = fernet.encrypt(data)

# save encrypted file
with open("secret.enc", "wb") as file:
    file.write(encrypted)

print("File encrypted successfully!")