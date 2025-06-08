import time
import threading
import importlib
from flask import Flask, request
import config
import win32evtlog  # pywin32

app = Flask(__name__)
last_checkin = time.time()

def check_primary_heartbeat():
    global last_checkin
    server = 'localhost'
    logtype = 'Security'
    hand = win32evtlog.OpenEventLog(server, logtype)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    events = win32evtlog.ReadEventLog(hand, flags, 0)
    print([event.EventID for event in events])  # Debugging line

    for event in events:
        if event.EventID == config.EVENT_ID_LOGIN:
            event_time = time.mktime(event.TimeGenerated.timetuple())
            print(f"Event Time: {time.ctime(event_time)}, last_checkin: {time.ctime(last_checkin)}")  # Debugging line
            if event_time > last_checkin:
                last_checkin = event_time
                print(f"Primary heartbeat received at {time.ctime(event_time)}")
                break

def monitor_heartbeat():
    global last_checkin
    print("Monitoring primary heartbeat...")
    while True:
        check_primary_heartbeat()
        if time.time() - last_checkin > config.CHECKIN_TIMEOUT:
            print("DEAD MAN SWITCH TRIGGERED")
            run_payloads()
            time.sleep(60)  # Cooldown
        time.sleep(5)

def run_payloads():
    for payload_str in config.PAYLOADS:
        module_name, func_name = payload_str.split(':')
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        try:
            func()
        except Exception as e:
            print(f"[Payload Error] {e}")

@app.route('/heartbeat', methods=['GET', 'POST'])
def heartbeat():
    global last_checkin
    password = request.values.get('password')
    if password == config.HEARTBEAT_PASSWORD:
        last_checkin = time.time()
        return f'Heartbeat received: {time.ctime(last_checkin)}', 200
    return 'Forbidden', 403

def start_server():
    app.run(host='0.0.0.0', port=config.SECONDARY_PORT)

if __name__ == '__main__':
    threading.Thread(target=monitor_heartbeat, daemon=True).start()
    start_server()
