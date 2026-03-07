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
    """
    Purpose: Performs the game download. Intended to be run in a thread.
    Preconditions:
        url: string, URL to download game from
        stop_flag: A reference to a dictionary formatted as {"stop": False}. If it is set to True, the download will quit early.
        progressbar: Reference to a UI window where the progress bar is shown.
    Postconditons:  
        LCE will be downloaded into LegacyLauncher/Minecraft_LCE
        No ZIP file should be leftover
    """
    zip_path = "LegacyLauncher/LCEWindows64.zip"
    
    print("Download started...")
    
    # Download the file
    with requests.get(url, stream=True) as r:
        r.raise_for_status() # Raise error if download fails
        total_size = int(r.headers.get("Content-Length", 0)) # Get size of file
        chunk_size = 1024 # 1KB chunks
        num_chunks = total_size // chunk_size + 1
        
        # Create needed paths
        extract_path = "LegacyLauncher/Minecraft_LCE"
        os.makedirs(extract_path, exist_ok=True)
        
        # Download file, chunk-by-chunk
        with open(zip_path, "wb") as f:
            for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                # if the user closes the download window, stop
                if stop_flag["stop"]:
                    print("Download cancelled")
                    break
                # If chunk is valid, save it
                if chunk:
                    f.write(chunk)
                    # Update UI
                    progress.set((i+1) / num_chunks * 100)
                    progress_str.set(f"{(i+1) // 1000}/{num_chunks // 1000} MB downloaded")
   
    # If download wasn't cancelled, start unzipping
    if not stop_flag["stop"]:
        progress_str.set(f"Uncompressing...")
        print("Unzipping...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
    
    # Delete the zip file
    progress_str.set("Cleaning up...")
    print("Cleaning up (removing zip file)...")
    os.remove(zip_path)
    print(f"Downloaded & extracted LCE into {extract_path}")
    
    # Reset UI
    progress_str.set("")
    progress.set(0)
    # Delete progressbar window
    if not stop_flag["stop"]:
        progressbar.after(0, progressbar.destroy)


def download_game(url):
    """
    Purpose: Download LCE in the background, and display a progress bar
    Percondition:
        url: string, URL to download game from
    Postcondition:
        Game will be downloaded into LegacyLauncher/Minecraft_LCE
    """
    # Create window for progress bar
    root = Toplevel()
    root.title = ("Download Progress")
    root.geometry(get_geometry_centred(280, 70))
    root.resizable(False, False)
    
    # Makes the window the "focus", don't let user interact with main window while downloading
    root.transient(window)
    root.grab_set()
    
    counter = Label(root, textvariable=progress_str)
    counter.pack(padx=10, pady=10)

    bar = ttk.Progressbar(root, variable=progress, maximum=100)
    bar.pack(padx=10, pady=(0, 10), fill="x")
    
    stop_flag = {"stop": False} # mutable so that thread will detect change
    
    # If user closes the progress window, signal the download thread to stop
    def on_close():
        stop_flag["stop"] = True
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    
    # Start download thread
    Thread(target=lambda: perform_download(url, stop_flag, root), daemon=True).start()
    

def get_geometry_centred(w, h):
    """
    Purpose: Calculate geometry to place a window in the centre of the screen
    Preconditions:
        w: int, width of window you are positioning
        h: int, height of window
    Returns: string, tkinter geometry for window
    """

    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    x = (screen_w - w) // 2
    y = (screen_h - h) // 2

    return f"{w}x{h}+{x}+{y}"

# Create main window
window.title("LegacyLauncher")

window.geometry(get_geometry_centred(380, 240))
window.resizable(False, False)

frame = Frame(window)
frame.pack(expand=True)

name = StringVar()
servername=StringVar()
ip = StringVar()
port = StringVar()
verified_url = StringVar()

# General option label

general_lb = Label(frame, text="General Options")
general_lb.grid(row=0, column=0, columnspan=2, pady=(10, 5))

# Username input

name_lb = Label(frame, text="Player Name (can be anything):")
name_lb.grid(row=1, column=0, padx=10, pady=0)

name_ent = Entry(frame, textvariable=name)
name_ent.grid(row=1, column=1, padx=0, pady=0)

# Multiplayer label

multi_lb = Label(frame, text="Server Options")
multi_lb.grid(row=2, column=0, columnspan=2, pady=(10, 5))

# Server name input

servername_lb = Label(frame, text="Server Name (can be anything):")
servername_lb.grid(row=3, column=0, padx=0, pady=0)

servername_ent = Entry(frame, textvariable=servername)
servername_ent.grid(row=3, column=1, padx=0, pady=0)

# IP address input

ip_lb = Label(frame, text="Server IP Address:")
ip_lb.grid(row=4, column=0, padx=0, pady=0)

ip_ent = Entry(frame, textvariable=ip)
ip_ent.grid(row=4, column=1, padx=0, pady=0)

# Port input

port_lb = Label(frame, text="Server Port:")
port_lb.grid(row=5, column=0, padx=0, pady=0)

port_ent = Entry(frame, textvariable=port)
port_ent.grid(row=5, column=1, padx=0, pady=0)

def launch():
    # Launches the game with custom username
    command = ["./LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe", "-name", name.get()]
    subprocess.Popen(command)

# Create button UI area
footer = Frame(frame)
footer.grid(row=6, column=0, columnspan=2, pady=(20, 10))

# Singleplayer button

singleplayer_button = Button(footer, text="Launch Minecraft LCE", command=launch)
singleplayer_button.grid(row=0, column=0, padx=5)

def download_popup(info: str):
    """
    Purpose: Show a popup to download LCE. Will give options to download nightly build or verified archive.
    Preconditions:
        info: string, the information to display in the window at the top
    Postconditions: A new window will be opened
    """
    # Create the window
    root = Toplevel()
    root.title = ("Download Required")
    root.geometry(get_geometry_centred(360, 170))
    root.resizable(False, False)
    
    # Make window the focused window, so you can't interact with main window until closing it
    root.transient(window)
    root.grab_set()
    
    # Info label
    label = Label(root, text=info)
    label.pack(pady=(10, 5))
    
    # Downloads the nightly build
    def start_download_nightly():
        download_game("https://github.com/smartcmd/MinecraftConsoles/releases/download/nightly/LCEWindows64.zip")
        root.destroy()
    
    # Downloads the verified archive
    def start_download_verified():
        download_game(verified_url.get())
        root.destroy()
    
    # Button for verified archive
    verified_button = Button(root, text="✅ Download Latest Verified Archive", command=start_download_verified)
    verified_button.pack(pady=(0,5))
    
    # Button for nighly build
    nightly_button = Button(root, text="🌙 Download Latest Nightly Build", command=start_download_nightly)
    nightly_button.pack(pady=0)
    
    # Input for verified archive URL
    url_label = Label(root, text="Verified archive will download from:")
    url_label.pack(pady=(5,0))

    url_ent = Entry(root, textvariable=verified_url, width=48)
    url_ent.pack(pady=0)

# Check if game exists, send download popup if it doesn't
if not os.path.exists("LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe"):
    download_popup("No Minecraft LCE install was found.\nChoose at option below to download it automagically!")

# Does options file exist? If not, make it.
if not os.path.exists("LegacyLauncher/options.txt"):
    os.makedirs("LegacyLauncher", exist_ok=True)

    with open("LegacyLauncher/options.txt", "w") as f:
        f.write("Steve\nhttps://github.com/hw2007/LCE-Verified-Archive/releases/download/Latest/LCEWindows64.zip")

# Does servers file exist? If not, make it.
if not os.path.exists("LegacyLauncher/Minecraft_LCE/servers.txt"):
    os.makedirs("LegacyLauncher/Minecraft_LCE", exist_ok=True)

    with open("LegacyLauncher/Minecraft_LCE/servers.txt", "w") as f:
        f.write("127.0.0.1\n25565\nServer")

# Read options file
f = open("LegacyLauncher/options.txt", "r")
options = [L.rstrip() for L in f]
f.close()

# Read servers file
f = open("LegacyLauncher/Minecraft_LCE/servers.txt", "r")
server = [L.rstrip() for L in f]

# Load options & servers
name.set(options[0])
verified_url.set(options[1])
servername.set(server[2])
ip.set(server[0])
port.set(server[1])

# Save options & servers
def save_config(*args):
    with open("LegacyLauncher/options.txt", "w") as f:
        f.write(f"{name.get()}\n{verified_url.get()}")
    with open("LegacyLauncher/Minecraft_LCE/servers.txt", "w") as f:
        f.write(f"{ip.get()}\n{port.get()}\n{servername.get()}")

# Make save_config run whenever text inputs are changed
name.trace_add("write", save_config)
servername.trace_add("write", save_config)
ip.trace_add("write", save_config)
port.trace_add("write", save_config)
verified_url.trace_add("write", save_config)

# Open popup to update LCE
def update():
    download_popup("Where should Minecraft LCE be downloaded from?\nChoose one of the options below:")

# Button to open update popup
update_button = Button(footer, text="📥 Update LCE", command=update)
update_button.grid(row=0, column=2, padx=5)

# GO GO GO
window.mainloop()

