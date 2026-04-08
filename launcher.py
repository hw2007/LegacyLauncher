# Minecraft legacy console edition launcher by hw2007

from tkinter import *
from tkinter import ttk
import os
import sys
import subprocess
import requests
from threading import Thread

import downloader as dl

CONFIG_VERSION = 2
RELEASE_TAG = "v1.3"

DOWNLOAD_SOURCES = {
    "archive": "https://github.com/hw2007/LCE-Verified-Archive/releases/download/Latest/LCEWindows64.zip",
    "nightly": "https://github.com/MCLCE/MinecraftConsoles/releases/download/nightly/LCEWindows64.zip",
    "custom": "" # Will be loaded later
}


window = Tk()


def check_for_launcher_update() -> bool:
    """
    Purpose: Check if there is a new launcher update available
    Returns: bool, True if there is an update, False otherwise
    """
    url = "https://api.github.com/repos/hw2007/LegacyLauncher/releases/latest"
    response = requests.get(url)
    data = response.json()

    latest_tag = data["tag_name"]

    return latest_tag != RELEASE_TAG


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
    Thread(target=lambda: dl.perform_download(url, stop_flag, root, progress_str, progress), daemon=True).start()


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


def launch():
    # Launches the game with custom username
    command = ["./LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe", "-name", name.get()]
    subprocess.Popen(command)


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


# Set window icon
icon = PhotoImage(file=resource_path("icon.png"))
window.iconphoto(True, icon)

# Create main window
window.title("LegacyLauncher")

window.geometry(get_geometry_centred(290, 160))
window.resizable(False, False)

frame = Frame(window)
frame.pack(expand=True)

# Defining tk variables

name = StringVar()
custom_url = StringVar()
fullscreen = BooleanVar()
uid = StringVar()
progress = DoubleVar()
progress_str = StringVar()
download_source = StringVar()

# Username input

name_lb = Label(frame, text="Player Name (can be anything):")
name_lb.pack(pady=(10,0))

name_ent = Entry(frame, textvariable=name)
name_ent.pack(pady=0)

# Fullscreen toggle

full_check = Checkbutton(frame, text="Launch in Fullscreen", variable=fullscreen)
full_check.pack(pady=10)

# Create button UI area
footer = Frame(window)
footer.pack()

# Singleplayer button
singleplayer_button = Button(footer, text="Launch Minecraft LCE", command=launch)
singleplayer_button.grid(row=0, column=0, padx=5)

# Button to open update popup
update_button = Button(footer, text="Update LCE", command=download_popup)
update_button.grid(row=0, column=1, padx=5)

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


def load_config():
    """
    Purpose: Load data from config file
    Postconditions: tk vars are modified to fit loaded config
    """
    # ver, name, custom URL, fullscreen?, download source
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
    if len(options) > 1:
        name.set(options[1])
    else:
        name.set(defaults[1])
        print("Cannot get name")
    if len(options) > 2:
        custom_url.set(options[2])
    else:
        custom_url.set(defaults[2])
        print("Cannot get URL")
    if len(options) > 3:
        fullscreen.set(options[3] == "True")
    else:
        fullscreen.set(defaults[3])
        print("Cannot get fullscreen")
    if len(options) > 4:
        download_source.set(options[4])
    else:
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


def save_config(*args):
    """
    Purpose: save the given data to the config file
    Preconditions: data is a list containing the data
    Postconditions: Data is saved to LegacyLauncher/options.txt in the same order as it appears in the list
    """
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

# Load config if exists, then save to ensure existence
load_config()
save_config()

# Check if game exists, send download popup if it doesn't
if not os.path.exists("LegacyLauncher/Minecraft_LCE/Minecraft.Client.exe"):
    download_popup()

# GO GO GO
window.mainloop()

