# Minecraft legacy console edition launcher by hw2007

from tkinter import *
from tkinter import ttk
import os
import requests
import zipfile
import subprocess
from threading import Thread

window = Tk()

progress = DoubleVar()
progress_str = StringVar()

def perform_download(url, stop_flag, progressbar):
    working_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(working_dir, "LCEWindows64.zip")
    
    print("Download started...")
        
    with requests.get(url, stream=True) as r:
        r.raise_for_status() # Raise error if download fails
        total_size = int(r.headers.get("Content-Length", 0))
        chunk_size = 1024 # 1KB chunks
        num_chunks = total_size // chunk_size + 1

        extract_path = os.path.join(working_dir, "LegacyLauncher/Minecraft_LCE")
        os.makedirs(extract_path, exist_ok=True)

        with open(zip_path, "wb") as f:
            for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                if stop_flag["stop"]:
                    print("Download cancelled")
                    break
                if chunk:
                    f.write(chunk)
                    progress.set((i+1) / num_chunks * 100)
                    progress_str.set(f"{(i+1) // 1000}/{num_chunks // 1000} MB downloaded")
    if not stop_flag["stop"]:
        progress_str.set(f"Uncompressing...")
        print("Unzipping...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
    
    progress_str.set("Cleaning up...")
    print("Cleaning up (removing zip file)...")
    os.remove(zip_path)
    print(f"Downloaded & extracted LCE into {extract_path}")
    
    progress_str.set("")
    progress.set(0)
    if not stop_flag["stop"]:
        progressbar.after(0, progressbar.destroy)


def download_game(url):
    root = Toplevel()
    root.title = ("Download Progress")
    root.geometry(get_geometry_centred(200, 70))
    root.resizable(False, False)

    root.transient(window)
    root.grab_set()
    
    counter = Label(root, textvariable=progress_str)
    counter.pack(padx=10, pady=10)

    bar = ttk.Progressbar(root, variable=progress, maximum=100)
    bar.pack(padx=10, pady=(0, 10), fill="x")
    
    stop_flag = {"stop": False} # mutable so that thread will detect change

    def on_close():
        stop_flag["stop"] = True
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
 
    Thread(target=lambda: perform_download(url, stop_flag, root), daemon=True).start()
    

def get_geometry_centred(w, h):
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    x = (screen_w - w) // 2
    y = (screen_h - h) // 2

    return f"{w}x{h}+{x}+{y}"

window.title("LegacyLauncher")

window.geometry(get_geometry_centred(420, 280))
window.resizable(False, False)

frame = Frame(window)
frame.pack(expand=True)

name = StringVar()
ip = StringVar()
port = StringVar()
verified_url = StringVar()

# General option label

general_lb = Label(frame, text="General Options")
general_lb.grid(row=0, column=0, columnspan=2, pady=10)

# Username input

name_lb = Label(frame, text="Player Name (can be anything):")
name_lb.grid(row=1, column=0, padx=10, pady=10)

name_ent = Entry(frame, textvariable=name)
name_ent.grid(row=1, column=1, padx=0, pady=10)

# Multiplayer label

multi_lb = Label(frame, text="Server Options")
multi_lb.grid(row=2, column=0, columnspan=2, pady=(20, 10))

# IP address input

ip_lb = Label(frame, text="Server IP Address:")
ip_lb.grid(row=3, column=0, padx=10, pady=10)

ip_ent = Entry(frame, textvariable=ip)
ip_ent.grid(row=3, column=1, padx=0, pady=10)

# Port input

port_lb = Label(frame, text="Server Port:")
port_lb.grid(row=4, column=0, padx=10, pady=(0, 10))

port_ent = Entry(frame, textvariable=port)
port_ent.grid(row=4, column=1, padx=0, pady=(0, 10))

def launch():
    command = ["./LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe", "-name", name.get()]
    subprocess.Popen(command)

def launch_multiplayer():
    command = ["./LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe", "-name", name.get(), "-ip", ip.get(), "-port", port.get()]
    subprocess.Popen(command)

# Create button UI area
footer = Frame(frame)
footer.grid(row=5, column=0, columnspan=2, pady=(20, 10))

# Singleplayer button

singleplayer_button = Button(footer, text="Launch normally", command=launch)
singleplayer_button.grid(row=0, column=0, padx=5)

# Multiplayer button

multiplayer_button = Button(footer, text="Launch into server", command=launch_multiplayer)
multiplayer_button.grid(row=0, column=1, padx=5)

def download_popup(info: str): # info string will be displayed above download buttons
    root = Toplevel()
    root.title = ("Download Required")
    root.geometry(get_geometry_centred(360, 220))
    root.resizable(False, False)

    root.transient(window)
    root.grab_set()

    label = Label(root, text=info)
    label.pack(pady=10)

    def start_download_nightly():
        download_game("https://github.com/smartcmd/MinecraftConsoles/releases/download/nightly/LCEWindows64.zip")
        root.destroy()

    def start_download_verified():
        download_game(verified_url.get())
        root.destroy()

    verified_button = Button(root, text="✅ Download Latest Verified Archive", command=start_download_verified)
    verified_button.pack(pady=(10,0))
    
    nightly_button = Button(root, text="🌙 Download Latest Nightly Build", command=start_download_nightly)
    nightly_button.pack(pady=10)

    url_label = Label(root, text="Verified archive will download from:")
    url_label.pack(pady=(10,0))

    url_ent = Entry(root, textvariable=verified_url, width=48)
    url_ent.pack(pady=10)

# Check if game exists, send download popup if it doesn't
if not os.path.exists("LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe"):
    download_popup("No Minecraft LCE install was found.\nChoose at option below to download it automagically!")

if not os.path.exists("LegacyLauncher/options.txt"):
    os.makedirs("LegacyLauncher", exist_ok=True)

    with open("LegacyLauncher/options.txt", "w") as f:
        f.write("Steve\n0.0.0.0\n25565\nhttps://github.com/hw2007/LCE-Verified-Archive/releases/download/Latest/LCEWindows64.zip")

f = open("LegacyLauncher/options.txt", "r")
filedata = [L.rstrip() for L in f]
f.close()
print(filedata)
name.set(filedata[0])
ip.set(filedata[1])
port.set(filedata[2])
verified_url.set(filedata[3])

def save_config(*args):
    with open("LegacyLauncher/options.txt", "w") as f:
        f.write(f"{name.get()}\n{ip.get()}\n{port.get()}\n{verified_url.get()}")

name.trace_add("write", save_config)
ip.trace_add("write", save_config)
port.trace_add("write", save_config)
verified_url.trace_add("write", save_config)

def update():
    download_popup("Where should Minecraft LCE be downloaded from?\nChoose one of the options below:")

update_button = Button(footer, text="📥 Update LCE", command=update)
update_button.grid(row=0, column=2, padx=5)

window.mainloop()

