# LegacyLauncher
Launcher for Minecraft: Legacy Console Edition

<img width="292" height="192" alt="image" src="https://github.com/user-attachments/assets/9dde98b5-6f1a-4a61-b000-9a6734122f9a" />

# Purpose
This is intended to be a super simple & crude launcher for Minecraft LCE. It allows you download LCE automatically, to submit a username, choose fullscreen options, then launch or update LCE.

# Installation
## ❗ After installation, please read the setup instructions which are further down this page.
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
Note: LegacyLauncher is not regularily tested on macOS. Please write a report if there are any issues.
1. Follow steps 1-4 for the Windows instructions
2. Download & install <a href=https://getwhisky.app/>Whisky</a>
3. Create a new bottle inside of Whisky. Leave all settings default (name can be whatever you want).
4. Open LegacyLauncher.exe. If it isn't working, make sure you are opening it with Whisky.

### Manual Building
1. Download the source code
2. Ensure you have python 3.x and pyinstaller installed.
3. Open the project directory in your terminal, and run `pyinstaller LegacyLauncher.spec` to create a build for your operating system.

Note: While you can technically create native builds for linux & macOS, this is not officially supported and you will not be able to simply run LCE that way since there are only windows builds available.

# Setup
After installing & running, you will be prompted to download Minecraft LCE. You will have the option to use the latest verified archive, or one of two different nightly builds. The verified archive is guarenteed to be functional, and exists so that it is easier for server owners to ensure clients are connecting from the same build.

### Link to repos used for nightly builds:

<a href=https://github.com/itsRevela/LCE-Revelations>itsRevela/LCE-Revelations</a> (this is where my verified archives come from as well)

<a href=https://github.com/MCLCE/MinecraftConsoles>MCLCE/MinecraftConsoles</a>

# Updating LegacyLauncher
To update an existing install of legacy launcher, simply... 
1. Go to the <a href=https://github.com/hw2007/LegacyLauncher/releases/latest>latest release</a>
2. Follow the instructions on the release page
