import subprocess

def get_active_process():
    pid = subprocess.check_output(["xdotool", "getactivewindow"]).decode('utf-8')
    name = subprocess.check_output(["xprop", "-id", pid, "WM_CLASS"]).decode("utf-8").strip().split(',')[-1].replace('"', '').strip()
    return name.lower()
