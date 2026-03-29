# Minecraft legacy console edition launcher by hw2007

from tkinter import *
from tkinter import ttk
import os
import sys
import requests
import zipfile
import subprocess
from threading import Thread

CONFIG_VERSION = 2

DOWNLOAD_SOURCES = {
    "archive": "https://github.com/hw2007/LCE-Verified-Archive/releases/download/Latest/LCEWindows64.zip",
    "nightly": "https://github.com/smartcmd/MinecraftConsoles/releases/download/nightly/LCEWindows64.zip",
    "custom": "" # Will be loaded later
}


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

download_source = StringVar()


def perform_download(url, stop_flag, progressbar):
    """
    Purpose: Performs the game download. Intended to be run in a thread.
    Preconditions:
        url: string, URL to download game from
        stop_flag: A reference to a dictionary formatted as {"stop": False}. If it is set to True, the download will quit early.
        progressbar: Reference to a UI window where the progress bar is shown.
    Postconditons:  
        LCE will be downloaded into LegacyLauncher/Minecraft_LCE. If is_update is True, we are only downloading the Minecraft.Client.exe
        No ZIP file should be leftover
    """
    download_path = "LegacyLauncher/temp_download.zip"
    
    print("Download started...")
    
    # Download the file
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status() # Raise error if download fails
            total_size = int(r.headers.get("Content-Length", 0)) # Get size of file
            chunk_size = 1024 # 1KB chunks
            num_chunks = total_size // chunk_size  + 1
            
            # Create needed paths
            minecraft_path = "LegacyLauncher/Minecraft_LCE"
            os.makedirs(minecraft_path, exist_ok=True)
            
            # Download file, chunk-by-chunk
            with open(download_path, "wb") as f:
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
    except:
        progress_str.set("Error! Couldn't download file.")
        return
    
    # If download wasn't cancelled, start unzipping
    try:
        if not stop_flag["stop"]:
            progress_str.set(f"Uncompressing...")
            print("Unzipping...")
            with zipfile.ZipFile(download_path, "r") as zip_ref:
                zip_ref.extractall(minecraft_path)
    except:
        progress_str.set("Error! Couldn't uncompress file.")
        return
    
    # Delete the zip file
    progress_str.set("Cleaning up...")
    print("Cleaning up (removing zip file)...")
    os.remove(download_path)
    print(f"Downloaded & extracted LCE into {minecraft_path}")
    
    # Delete progressbar window
    if not stop_flag["stop"]:
        progressbar.after(0, progressbar.destroy)


def download_game(url):
    """
    Purpose: Download LCE in the background, and display a progress bar
    Percondition:
        url: string, URL to download game fromLegacyLauncher/Minecraft_LCE
    Postcondition:
        Game will be downloaded into LegacyLauncher/Minecraft_LCE.
    """

    # Create window for progress bar
    root = Toplevel()
    root.title = ("Download Progress")
    root.geometry(get_geometry_centred(280, 108))
    root.resizable(False, False)
    
    # Makes the window the "focus", don't let user interact with main window while downloading
    root.transient(window)
    root.grab_set()
    
    counter = Label(root, textvariable=progress_str)
    counter.pack(padx=10, pady=10)

    # Progress bar
    bar = ttk.Progressbar(root, variable=progress, maximum=100)
    bar.pack(padx=10, pady=(0, 10), fill="x")
    
    # If user closes the progress window, signal the download thread to stop
    def on_close():
        progress_str.set("")
        progress.set(0)
        stop_flag["stop"] = True
        root.destroy()

    # Cancel button
    cancel_button = Button(root, text="Cancel", command=on_close)
    cancel_button.pack()
    
    stop_flag = {"stop": False} # mutable so that thread will detect change

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
custom_url = StringVar()
fullscreen = BooleanVar()

uid = StringVar()

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
    subprocess.Popen(command)

# Create button UI area
footer = Frame(window)
footer.pack()

# Singleplayer button

singleplayer_button = Button(footer, text="Launch Minecraft LCE", command=launch)
singleplayer_button.grid(row=0, column=0, padx=5)


def download_popup():
    """
    Purpose: Show a popup to download LCE. Will give options to download nightly build or verified archive.
    Preconditions:
        info: string, the information to display in the window at the top
    Postconditions: A new window will be opened
    """
    
    # Create the window
    root = Toplevel()
    root.title = ("Download Required")
    root.geometry(get_geometry_centred(330, 200))
    root.resizable(False, False)
    
    # Make window the focused window, so you can't interact with main window until closing it
    root.transient(window)
    root.grab_set()
    
    # Info label
    label = Label(root, text="Choose a version of LCE to install automagically:")
    label.pack(pady=(10, 0))
    
    # Downloads the nightly build
    def start_download():
        download_game(DOWNLOAD_SOURCES[download_source.get()])
        root.destroy()
    
    # Updates the state of custom download options
    def update_state():
        if download_source.get() == "custom":
            url_label.config(state="normal")
            url_ent.config(state="normal")
        else:
            url_label.config(state="disabled")
            url_ent.config(state="disabled")
    
    radios = Frame(root)
    radios.pack(pady=(0,10))

    # Button for verified archive
    verified_button = Radiobutton(radios, text="Verified Archive", variable=download_source, value="archive", command=update_state)
    verified_button.pack(anchor='w')
    
    # Button for nighly build
    nightly_button = Radiobutton(radios, text="Nightly Build", variable=download_source, value="nightly", command=update_state)
    nightly_button.pack(anchor='w')

    # Button for custom source
    custom_button = Radiobutton(radios, text="Custom", variable=download_source, value="custom", command=update_state)
    custom_button.pack(anchor='w')

    # Input for custom full URL
    url_label = Label(root, text="Custom install URL:", state="disabled")
    url_label.pack()

    url_ent = Entry(root, textvariable=custom_url, width=44, state="disabled")
    url_ent.pack()

    update_state()

    buttons = Frame(root)
    buttons.pack(pady=10)

    def cancel():
        root.destroy()

    # Cancel button
    cancel_button = Button(buttons, text="Cancel", command=cancel)
    cancel_button.grid(column=0, row=0, padx=5)

    # Download button
    download_button = Button(buttons, text="Start Download", command=start_download)
    download_button.grid(column=1, row=0, padx=5)


#### DEAL WITH CONFIG FILES ####

# Check if game exists, send download popup if it doesn't
if not os.path.exists("LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe"):
    download_popup()

defaults = [CONFIG_VERSION, "Steve", "", True, "archive"]

# Read options file
try:
    f = open("LegacyLauncher/options.txt", "r")
    options = [L.rstrip() for L in f]
    if not options[0].isdigit(): # Detect older config format which doesn't include a version at the top. WARNING: This will run into issues if the player set their usename to only numbers. Oh, bother...
        print("Unversioned config detected")
        options.insert(0, "0")
    if int(options[0]) <= 1:
         print("Version 1 config detected, migrating...")
         options.append(defaults[4])
    f.close()
except:
    print("Error opening options.txt")

# Load options & servers
try:
    name.set(options[1])
except:
    name.set(defaults[1])
    print("Cannot get name")
try:
    custom_url.set(options[2])
except:
    custom_url.set(defaults[2])
    print("Cannot get URL")
try:
    fullscreen.set(options[3] == "True")
except:
    fullscreen.set(defaults[3])
    print("Cannot get fullscreen")
try:
    download_source.set(options[4])
except:
    download_source.set(defaults[4])
    print("Cannot get download source")

# Try to read UID
try:
    f = open("LegacyLauncher/Minecraft_LCE/uid.dat", 'r')
    data = list(f)
    f.close()
    uid.set(data[0].rstrip())
except:
    uid.set("Unknown, run game to generate")
    print("Cannot get UID")

# Save options & servers
def save_config(*args):
    DOWNLOAD_SOURCES["custom"] = custom_url.get()

    os.makedirs("LegacyLauncher/Minecraft_LCE", exist_ok=True)

    with open("LegacyLauncher/options.txt", "w") as f:
        f.write(f"{CONFIG_VERSION}\n{name.get()}\n{custom_url.get()}\n{fullscreen.get()}\n{download_source.get()}")
    with open("LegacyLauncher/Minecraft_LCE/options.txt", "w") as f:
        data = ""
        if fullscreen.get():
            data = "fullscreen=1"
        else:
            data = "fullscreen=0"
        f.write(data)

# Make save_config run whenever text inputs are changed
name.trace_add("write", save_config)
custom_url.trace_add("write", save_config)
fullscreen.trace_add("write", save_config)
download_source.trace_add("write", save_config)

save_config()

# Open popup to update LCE
def update():
    download_popup()

# Button to open update popup
update_button = Button(footer, text="Update LCE", command=update)
update_button.grid(row=0, column=1, padx=5)

def copy_uid():
    # Purpose: copy the UID to the clipboard
    window.clipboard_clear()
    window.clipboard_append(uid.get())

def edit_uid_window(): 
    uid_temp = StringVar()
    uid_temp.set(uid.get())

    # Create window for progress bar
    root = Toplevel()
    root.title = ("Edit UID")
    root.geometry(get_geometry_centred(210, 80))
    root.resizable(False, False)
    
    # Makes the window the "focus", don't let user interact with main window while downloading
    root.transient(window)
    root.grab_set()
     
    def save_uid():
        os.makedirs("LegacyLauncher/Minecraft_LCE/", exist_ok=True)
        with open("LegacyLauncher/Minecraft_LCE/uid.dat", 'w') as f:
            f.write(uid_temp.get())
        uid.set(uid_temp.get())

        root.destroy()
    
    def cancel():
        root.destroy()

    uid_ent = Entry(root, textvariable=uid_temp, width=24)
    uid_ent.pack(pady=10)

    tools = Frame(root)
    tools.pack()

    cancel = Button(tools, text="Cancel", command=cancel)
    cancel.grid(row=1, column=0, padx=5)

    submit = Button(tools, text="Submit", command=save_uid)
    submit.grid(row=1, column=1, padx=5)

# UID indicator
uid_frame = Frame(window)
uid_frame.pack()

uid_label = Label(uid_frame, text="UID:", fg="gray")
uid_label.grid(row=0, column=0, pady=0)

uid_val = Label(uid_frame, textvariable=uid, fg="gray")
uid_val.grid(row=0, column=1)

uid_edit = Button(uid_frame, text="edit", borderwidth=0, padx=0, pady=4, command=edit_uid_window)
uid_edit.grid(row=0, column=2)

uid_copy = Button(uid_frame, text="copy", borderwidth=0, padx=0, pady=4, command=copy_uid)
uid_copy.grid(row=0, column=3)

# GO GO GO
window.mainloop()

