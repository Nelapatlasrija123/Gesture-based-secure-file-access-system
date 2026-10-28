from cryptography.fernet import Fernet
import os
import time

# load key
with open("key.key", "rb") as key_file:
    key = key_file.read()

fernet = Fernet(key)

# read encrypted file
with open("secret.enc", "rb") as file:
    encrypted_data = file.read()

# decrypt
decrypted = fernet.decrypt(encrypted_data)

# create temporary file
with open("temp_secret.txt", "wb") as file:
    file.write(decrypted)

# open the file
os.startfile("temp_secret.txt")

print("File opened... closing in 10 seconds")

time.sleep(10)

# delete the temporary file
os.remove("temp_secret.txt")

print("Temporary file deleted")