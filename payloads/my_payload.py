import subprocess

def run():
    print("Running payload...")
    # Example: open file, send alert, run external script
    subprocess.run(["powershell", "-Command", "Start-Process notepad.exe"])
