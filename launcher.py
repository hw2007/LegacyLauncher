# Minecraft legacy console edition launcher by hw2007

from tkinter import *
import os
import requests
import zipfile
import time
import subprocess


def download_game():
    url = "https://github.com/smartcmd/MinecraftConsoles/releases/download/nightly/LCEWindows64.zip"
    
    working_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(working_dir, "LCEWindows64.zip")
    
    print("Download started...")
    response = requests.get(url)
    response.raise_for_status() # raise error if download fails
    
    extract_path = os.path.join(working_dir, "LegacyLauncher/Minecraft_LCE")
    os.makedirs(extract_path, exist_ok=True)
    
    with open(zip_path, "wb") as f:
        f.write(response.content)
    
    print("Unzipping...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    
    os.remove(zip_path)
    print(f"Downloaded & extracted LCE into {extract_path}")\


window = Tk()

dpi = window.winfo_fpixels("1i")
scale = dpi / 72
window.tk.call("tk", "scaling", dpi / 48)

def get_geometry_centred(w, h):
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    x = (screen_w - w) // 2
    y = (screen_h - h) // 2

    return f"{w}x{h}+{x}+{y}"

window.title("LegacyLauncher")

window.geometry(get_geometry_centred(int(450 * scale), int(250 * scale)))
window.resizable(False, False)

frame = Frame(window)
frame.pack(expand=True)

name = StringVar()
ip = StringVar()
port = StringVar()

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

# Singleplayer button

singleplayer_button = Button(frame, text="Launch normally", command=launch)
singleplayer_button.grid(row=5, column=0, pady=(20, 10), padx=5)

# Multiplayer button

multiplayer_button = Button(frame, text="Launch into server", command=launch_multiplayer)
multiplayer_button.grid(row=5, column=1, pady=(20, 10), padx=5)

def download_popup():
    root = Toplevel()
    root.title = ("Download Required")
    root.geometry(get_geometry_centred(int(440 * scale), int(180 * scale)))
    root.resizable(False, False)

    root.transient(window)
    root.grab_set()

    label = Label(root, text="No Minecraft LCE install was found.\nChoose at option below to download it automagically!\n(will be stored in a folder alongside this executable)")
    label.pack(pady=10)

    def start_download():
        download_game()
        root.destroy()

    dl_button = Button(root, text="Download Latest Nightly Build", command=start_download)
    dl_button.pack(pady=10)

    warning = Label(root, text="The launcher will freeze for multiple minutes while downloading.\nPlease be patient!")
    warning.pack(pady=10)

# Check if game exists, send download popup if it doesn't
if not os.path.exists("LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe"):
    download_popup()

if not os.path.exists("LegacyLauncher/options.txt"):
    os.makedirs("LegacyLauncher", exist_ok=True)

    with open("LegacyLauncher/options.txt", "w") as f:
        f.write("Steve\n0.0.0.0\n25565")

f = open("LegacyLauncher/options.txt", "r")
filedata = [L.rstrip() for L in f]
f.close()
print(filedata)
name.set(filedata[0])
ip.set(filedata[1])
port.set(filedata[2])

def save_config(*args):
    with open("LegacyLauncher/options.txt", "w") as f:
        f.write(f"{name.get()}\n{ip.get()}\n{port.get()}")

name.trace_add("write", save_config)
ip.trace_add("write", save_config)
port.trace_add("write", save_config)

window.mainloop()

