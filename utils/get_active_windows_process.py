import psutil
import win32process
import win32gui

def get_active_process():
    active_window = win32gui.GetForegroundWindow()
    pid = win32process.GetWindowThreadProcessId(active_window)
    return psutil.Process(pid[-1]).name()
