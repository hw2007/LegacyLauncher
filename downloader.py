import requests
import zipfile
import os
import shutil
import tempfile


def perform_download(url, stop_flag, progressbar, progress_str, progress):
    """
    Purpose: Performs the game download. Intended to be run in a thread.
    Preconditions:
        url: string, URL to download game from
        stop_flag: A reference to a dictionary formatted as {"stop": False}. If it is set to True, the download will quit early.
        progressbar: Reference to a UI window where the progress bar is shown.
        progress_str: Reference to a Tk StringVar where progress message is stored
        progress: Reference to a Tk IntVar where progress is stored
    Postconditons:  
        LCE will be downloaded into LegacyLauncher/Minecraft_LCE. If is_update is True, we are only downloading the Minecraft.Client.exe
        No ZIP file should be leftover
    """
    download_path = "LegacyLauncher/temp_download.zip" # Temporary path for zip file
    
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
        progress_str.set("Download failed O_o")
        return
    
    # If download wasn't cancelled, start unzipping
    try:
        if not stop_flag["stop"]:
            progress_str.set("Uncompressing...")
        print("Unzipping...")

        with zipfile.ZipFile(download_path, "r") as zip_ref:
            names = zip_ref.namelist()

            # Get top-level entries in the zip
            top_levels = set()
            for name in names:
                clean = name.strip("/")

                if not clean:
                    continue

                top = clean.split("/")[0]
                top_levels.add(top)

            # Case: exactly one top-level folder
            if len(top_levels) == 1:
                print("Note: zip file contains a top-level folder")
                top_folder = list(top_levels)[0]

                # Extract to temp dir first
                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_ref.extractall(tmpdir)

                    wrapper_dir = os.path.join(tmpdir, top_folder)

                    # Move contents up into minecraft_path
                    for item in os.listdir(wrapper_dir):
                        src = os.path.join(wrapper_dir, item)
                        dst = os.path.join(minecraft_path, item)

                        # Overwrite if exists
                        if os.path.exists(dst):
                            if os.path.isdir(dst):
                                shutil.rmtree(dst)
                            else:
                                os.remove(dst)

                        shutil.move(src, dst)
            else:
                # Normal extraction
                zip_ref.extractall(minecraft_path)
    except:
        progress_str.set("Uncompressing failed ;(")
        return
    
    # Delete the zip file
    progress_str.set("Cleaning up...")
    print("Cleaning up (removing zip file)...")
    os.remove(download_path)
    print(f"Downloaded & extracted LCE into {minecraft_path}")
    
    # Delete progressbar window
    if not stop_flag["stop"]:
        progressbar.after(0, progressbar.destroy)