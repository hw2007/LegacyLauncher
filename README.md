# LegacyLauncher
Launcher for Minecraft: Legacy Console Edition

<img width="382" height="252" alt="image" src="https://github.com/user-attachments/assets/d308a5e4-f248-410d-87ae-b447c8fd44fc" />

# Purpose
This is intended to be a super simple & crude launcher for Minecraft LCE. It allows you to submit a username & server information, then launch or update LCE.

# Installation
### Windows
1. Click on the <a href=https://github.com/hw2007/LegacyLauncher/releases/latest>latest release</a>
2. Download LegacyLauncher.zip
3. Unzip the file
4. Move LegacyLauncher.exe to wherever you want (e.g. your desktop)
5. Open LegacyLauncher.exe. You will likely get a windows defender popup. Click more info and allow or open anyway.

### Linux
1. Follow steps 1-4 for the Windows instructions
2. Open steam, and add LegacyLauncher.exe as a non-steam game
3. Open the game properties, and force it to use Proton 10 for compatibility
4. If you are using Wayland, set the launch options to `PROTON_USE_WINED3D=1 %command%`
5. Open the launcher through steam

### macOS
1. Follow steps 1-4 for the Windows instructions
2. Download & install <a href=https://getwhisky.app/>Whisky</a>
3. Create a new bottle inside of Whisky. Leave all settings default (name can be whatever you want).
4. Open LegacyLauncher.exe. If it isn't working, make sure you are opening it with Whisky.

# Setup
After installing & running, you will be prompted to download Minecraft LCE. You will have the option to use the latest verified archive, or the latest nightly build. The verified archive is a version handpicked by me that I know works. If you are playing on someone's server, for example, they may have a different handpicked version for you to use. In this case, replace the URL at the bottom of the window with the one they gave you, and download the latest verified archive.

The latest nightly build is updated every day, and is sourced from <a href=https://github.com/smartcmd/MinecraftConsoles>smartcmd/MinecraftConsoles</a>.

# Updating LegacyLauncher
To update an existing install of legacy launcher, simply... 
1. Go to the <a href=https://github.com/hw2007/LegacyLauncher/releases/latest>latest release</a>
2. Download LegacyLauncher.zip
3. Unzip the file
4. Replace the old LegacyLauncher.exe with the new one from the unzipped file.
