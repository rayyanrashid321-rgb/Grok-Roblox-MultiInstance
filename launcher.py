"""
Grok Roblox Multi-Instance Launcher
Simple Windows tool that holds Roblox's singleton mutex
so multiple RobloxPlayerBeta.exe clients can run at once.

Usage:
1. Close all Roblox windows first.
2. Run this script (python launcher.py) and keep the window open.
3. Launch Roblox normally as many times as you want.
4. Close this window when you're done.

DISCLAIMER:
- This is for personal/educational use only.
- Roblox does not officially support multiple clients on one PC.
- Misuse (ban evasion, botting, exploiting, etc.) violates Roblox Terms of Service.
- You are responsible for how you use this tool.
- No warranties. Use at your own risk.
"""

import ctypes
import ctypes.wintypes as wintypes
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Windows constants
ERROR_ALREADY_EXISTS = 183
INFINITE = 0xFFFFFFFF
MUTEX_ALL_ACCESS = 0x1F0001

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Function prototypes
kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE

kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.WaitForSingleObject.restype = wintypes.DWORD

kernel32.ReleaseMutex.argtypes = [wintypes.HANDLE]
kernel32.ReleaseMutex.restype = wintypes.BOOL

kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

class RobloxMutexHolder:
    def __init__(self):
        self.mutex_handle = None
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return False, "Already running"

        self.mutex_handle = kernel32.CreateMutexW(None, True, "ROBLOX_singletonMutex")
        error = ctypes.get_last_error()

        if not self.mutex_handle:
            return False, f"Failed to create mutex. Error: {error}"

        if error == ERROR_ALREADY_EXISTS:
            # Check if we actually own it
            wait_result = kernel32.WaitForSingleObject(self.mutex_handle, 0)
            if wait_result not in (0, 0x80):  # WAIT_OBJECT_0 or WAIT_ABANDONED
                kernel32.CloseHandle(self.mutex_handle)
                self.mutex_handle = None
                return False, "Mutex already exists and is owned by another process. Close all Roblox first."

        self.running = True
        self.thread = threading.Thread(target=self._hold_mutex, daemon=True)
        self.thread.start()
        return True, "Mutex acquired successfully. You can now launch multiple Roblox clients."

    def _hold_mutex(self):
        # Keep the thread alive so the mutex stays owned
        while self.running:
            try:
                # Just sleep; ownership is held by this thread
                import time
                time.sleep(1)
            except:
                break

    def stop(self):
        self.running = False
        if self.mutex_handle:
            kernel32.ReleaseMutex(self.mutex_handle)
            kernel32.CloseHandle(self.mutex_handle)
            self.mutex_handle = None
        return "Mutex released."

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Grok Roblox Multi-Instance")
        self.root.geometry("520x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.holder = RobloxMutexHolder()

        # Title
        title = tk.Label(root, text="Grok Roblox Multi-Instance", font=("Segoe UI", 16, "bold"),
                         bg="#1e1e2e", fg="#cdd6f4")
        title.pack(pady=15)

        # Status
        self.status_label = tk.Label(root, text="Status: Stopped", font=("Segoe UI", 11),
                                      bg="#1e1e2e", fg="#f38ba8")
        self.status_label.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(root, bg="#1e1e2e")
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="Start Multi-Instance", command=self.start,
                                    bg="#a6e3a1", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                                    width=22, height=2, relief="flat")
        self.start_btn.pack(side=tk.LEFT, padx=8)

        self.stop_btn = tk.Button(btn_frame, text="Stop & Release", command=self.stop,
                                   bg="#f38ba8", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                                   width=22, height=2, relief="flat", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=8)

        # Log
        log_label = tk.Label(root, text="Log:", bg="#1e1e2e", fg="#bac2de", font=("Segoe UI", 10))
        log_label.pack(anchor="w", padx=20)

        self.log = scrolledtext.ScrolledText(root, height=12, width=60, bg="#313244", fg="#cdd6f4",
                                              font=("Consolas", 9), relief="flat", wrap=tk.WORD)
        self.log.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        self.log.config(state=tk.DISABLED)

        # Footer
        footer = tk.Label(root, text="Close all Roblox before starting. Keep this window open while playing.",
                          bg="#1e1e2e", fg="#6c7086", font=("Segoe UI", 8))
        footer.pack(pady=8)

        self.log_message("Ready. Close all Roblox windows, then click Start.")

    def log_message(self, msg):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def start(self):
        success, message = self.holder.start()
        self.log_message(message)
        if success:
            self.status_label.config(text="Status: Running (Mutex Held)", fg="#a6e3a1")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", message)

    def stop(self):
        message = self.holder.stop()
        self.log_message(message)
        self.status_label.config(text="Status: Stopped", fg="#f38ba8")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def on_closing(self):
        if self.holder.running:
            if messagebox.askyesno("Quit", "Multi-instance is active. Stop and release mutex?"):
                self.holder.stop()
        self.root.destroy()

def main():
    if sys.platform != "win32":
        print("This tool only works on Windows.")
        return

    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
