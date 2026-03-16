# Minecraft legacy console edition launcher by hw2007

from tkinter import *
from tkinter import ttk
import os
import sys
import requests
import zipfile
import subprocess
from threading import Thread

def resource_path(path):
    """
    Purpose: Return the path of a resource, no matter if running from source or from build
    Preconditions:
        path: string, a valid path to resource, relative to script
    Returns:
        string, absolute path to that resource
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

window = Tk()

# Set window icon
icon = PhotoImage(file=resource_path("icon.png"))
window.iconphoto(True, icon)

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

window.geometry(get_geometry_centred(290, 160))
window.resizable(False, False)

frame = Frame(window)
frame.pack(expand=True)

name = StringVar()
verified_url = StringVar()
fullscreen = BooleanVar()

# Username input

name_lb = Label(frame, text="Player Name (can be anything):")
name_lb.pack(pady=(10,0))

name_ent = Entry(frame, textvariable=name)
name_ent.pack(pady=0)

# Fullscreen toggle

full_check = Checkbutton(frame, text="Launch in Fullscreen", variable=fullscreen)
full_check.pack(pady=10)

def launch():
    # Launches the game with custom username
    command = ["./LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe", "-name", name.get()]
    if fullscreen.get():
        command.append("-fullscreen")
    subprocess.Popen(command)

# Create button UI area
footer = Frame(window)
footer.pack(expand=True)

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
    verified_button = Button(root, text="Download Latest Verified Archive", command=start_download_verified)
    verified_button.pack(pady=(0,5))
    
    # Button for nighly build
    nightly_button = Button(root, text="Download Latest Nightly Build", command=start_download_nightly)
    nightly_button.pack(pady=0)
    
    # Input for verified archive URL
    url_label = Label(root, text="Verified archive will download from:")
    url_label.pack(pady=(5,0))

    url_ent = Entry(root, textvariable=verified_url, width=48)
    url_ent.pack(pady=0)

# Check if game exists, send download popup if it doesn't
if not os.path.exists("LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe"):
    download_popup("No Minecraft LCE install was found.\nChoose at option below to download it automagically!")

# Read options file
try:
    f = open("LegacyLauncher/options.txt", "r")
    options = [L.rstrip() for L in f]
    f.close()
except:
    print("Error opening options.txt")

# Load options & servers
try:
    name.set(options[0])
except:
    name.set("Steve")
    print("Cannot get name")
try:
    verified_url.set(options[1])
except:
    verified_url.set("https://github.com/hw2007/LCE-Verified-Archive/releases/download/Latest/LCEWindows64.zip")
    print("Cannot get URL")
try:
    fullscreen.set(options[2] == "True")
except:
    fullscreen.set(True)
    print("Cannot get fullscreen")

# Save options & servers
def save_config(*args):
    os.makedirs("LegacyLauncher", exist_ok=True)

    with open("LegacyLauncher/options.txt", "w") as f:
        f.write(f"{name.get()}\n{verified_url.get()}\n{fullscreen.get()}")

# Make save_config run whenever text inputs are changed
name.trace_add("write", save_config)
verified_url.trace_add("write", save_config)
fullscreen.trace_add("write", save_config)

save_config()

# Open popup to update LCE
def update():
    download_popup("Where should Minecraft LCE be downloaded from?\nChoose one of the options below:")

# Button to open update popup
update_button = Button(footer, text="Update LCE", command=update)
update_button.grid(row=0, column=2, padx=5)

# GO GO GO
window.mainloop()

