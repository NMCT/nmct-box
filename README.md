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
```bash
nmct@box-43def3:~ $ nmct-box -h

NMCT-Box home: /home/nmct/nmct-box

nmct-box: NMCT Box installation and management tool
Usage: nmct-box <command> [options]

Installation:
          prepare        Prepare a freshly installed Raspbian OS
          install        Download and install the framework and all its dependencies
          reinstall      Delete the entire installation and reinstall including dependencies
          autoinstall    Prepare fresh OS and schedule install at next boot
          set-hostname   Auto-configure hostname

Services:
          start          Start all associated services
          stop           Start all associated services
          restart        Restart all associated services
          status         Show status of associated services
          enable         Configure all associated services for automatic startup
          disable        Disable automatic startup for all associated services
          run <service>          Run single service in foreground for debugging

Updating:
          update         Download and install updates, including dependencies
          refresh        Download and install updates of the framework only

```
