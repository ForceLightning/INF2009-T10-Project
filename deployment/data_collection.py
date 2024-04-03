import re
import cv2
import time
import base64
import subprocess
import pandas as pd

def init_camera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise IOError("Failed to initialize camera")

    return cap

def capture_image():

    for i in range(3):
        print(f"Capturing image in {3-i} seconds...")
        time.sleep(1)

    camera = init_camera()

    try:
        _, frame = camera.read()
        _, buffer = cv2.imencode('.jpg', frame)
        img_bytes = base64.b64encode(buffer).decode("utf-8")

    except:
        raise Exception("Failed to capture image")

    finally:
        camera.release()

    return img_bytes

def get_wifi_strength():

    print("\nAttempting to get wifi signal strength")

    return pd.read_csv("wifi_signal_strength.csv", header=None, names=['timestamp', 'bssid', 'ssid', 'signal_strength']) # Dummy data

    command = "sudo nmcli dev wifi rescan"
    subprocess.run(command, shell=True, check=True)

    command = r"sudo nmcli -g in-use,bssid,ssid,signal dev wifi list | grep SIT-POLY"
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    try:
        out = result.stdout.decode()
        aps = out.split("\n")

        wifi_signal_strength = []

        for ap in aps:
            try:
                # Now get the signal strength from the filtered output.
                # print(ap)
                r = re.compile(r"(\*)?:((?:(?:[0-9A-F]{2})\\:){5}[0-9A-F]{2}):(.*):(\d+)").search(ap)
                in_use, bssid, ssid, signal_strength = r.groups()
                bssid = bssid.replace("\\", "")
                timenow = time.strftime("%Y%m%d%H%M%S")
                wifi_signal_strength.append([timenow, bssid, ssid, signal_strength])

                # with open("wifi_signal_strength.csv", "a", encoding="utf-8") as f:
                #     bssid = bssid.replace("\\", "")
                #     timenow = time.strftime("%Y%m%d%H%M%S")
                #     f.write(f"{timenow}, {bssid}, {ssid}, {signal_strength}\n")
            except AttributeError:
                print("Regex failed to match for SIT-WIFI %s", ap)

        return pd.DataFrame(wifi_signal_strength, columns=["Time", "BSSID", "SSID", "Signal Strength"])
    except:
        print("Failed to get wifi signal strength")

def get_btoutput():

    print("\nAttempting to get bluetoothctl output")

    with open("btoutput.txt", "r", encoding="utf-8") as f2:
        return f2.readlines() # Dummy data

    command = "bluetoothctl scan le & sleep 5; kill $!"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)

    btoutput = []
    timenow = time.strftime("%Y%m%d%H%M%S")
    # f2.write(f"{timenow} - Scan start\n")
    output = result.stdout.decode()
    for line in output.splitlines():
        timenow = time.strftime("%Y%m%d%H%M%S")
        btoutput.append(f"{timenow} - {line}\n")
        if not line:
            break
    # timenow = time.strftime("%Y%m%d%H%M%S")
    # f2.write(f"{timenow} - Scan end\n")