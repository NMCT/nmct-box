# NMCT Box

## Installation 
- Make sure your user account has `sudo` permission but **don't** run the installer as root!
- If you previously installed in another location, you need to unset or change `$NMCT_HOME` before installation

```bash
git clone https://github.com/NMCT/nmct-box.git
cd nmct-box/scripts
./nmct-box.sh install
sudo reboot
```

### Updating
```bash
nmct-box update
```

### Preparing a complete Raspbian image
- Flash the official Raspbian image using <etcher.io> or `dd`
- Put a suitable `wpa_supplicant.conf`, `ssh` and [nmct-box.sh](scripts/) on the boot partition
- After boot, run `/boot/nmct-box.sh prepare` (as root or sudo user)
- Reboot and reconnect using the provided credentials
- Run `/boot/nmct-box.sh install`
- Reboot

## Usage
