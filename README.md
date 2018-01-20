# NMCT Box

## Installation 
- Make sure your user account has `sudo` permission but **don't** run the installer as root!
- If you previously installed in another location, you need to unset or change `$NMCT_HOME` before installation

```bash
git clone https://github.com/nmctseb/nmct-box.git
cd nmct-box/scripts
./install.sh
```

### Updating
```bash
cd nmct-box/scripts
git pull
./install.sh --nmct-only
```

### Preparing a complete Raspbian image
- Flash the official Raspbian image using <etcher.io> or `dd`
- Put a suitable `wpa_supplicant.conf`, `ssh` and [prepare_image.sh](scripts/) on the boot partition
- After boot, run `sudo /boot/prepare_image.sh`
- Wait ~2.5 hours 
- Note the credentials and hostname displayed before the reboot at the end!


## Usage
> write me!
