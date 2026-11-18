# GameSir Battery Addon for MangoHud

[![Tests](https://github.com/derekagraham78/mangohud-gamesir-battery/actions/workflows/tests.yml/badge.svg)](https://github.com/derekagraham78/mangohud-gamesir-battery/actions/workflows/tests.yml)

Display your GameSir controller's battery level in MangoHud when Linux does not
provide a battery reading for the receiver.

This addon runs a small Python reader outside the game and supplies the battery
percentage through MangoHud's existing `exec` option. **No MangoHud patch or
Deadband installation is required.**

## Supported hardware

| Controller | Connection and mode | USB ID | Status |
| --- | --- | --- | --- |
| GameSir G7 Pro 8K PC | 2.4 GHz receiver, XInput mode | `3537:10c6` | Tested on CachyOS |

Other GameSir controllers and receiver IDs are not supported yet. Bluetooth,
wired mode and PS4 mode are not supported. The addon does not correct the fixed
5% battery value some controllers report in PS4 mode.

Hardware testing returned 100% and 99% on the supported receiver. The full
discharge curve and charging flag have not been hardware-validated.

## Requirements

- Linux and Python 3.10 or newer.
- The `hidapi` Python bindings, which expose `hid.device()`.
- Read/write permission for the receiver's vendor `/dev/hidraw*` interface.
- MangoHud with `legacy_layout=0` and support for `exec`.

On Arch Linux or CachyOS, install the HID bindings with:

```sh
sudo pacman -S python-hidapi
```

For another distribution, use its package for the Python HIDAPI bindings. If
using a virtual environment, install `requirements.txt` there and run the
reader with that environment's Python. The generated user service runs the
system `python3`, so adjust its `ExecStart` if you choose a virtual environment.
The `--status` command needs only Python, without the HID bindings or device access.

## Install

```sh
git clone https://github.com/derekagraham78/mangohud-gamesir-battery.git
cd mangohud-gamesir-battery
python3 install.py
```

The installer copies the reader to
`~/.local/bin/mangohud-gamesir-battery`, generates a user service and writes a
MangoHud config example. It does not use sudo, install dependencies, change
your MangoHud config or start the service. It backs up existing installed
files with a `.bak` suffix when updating.

Power on the controller in 2.4 GHz XInput mode and test one reading:

```sh
~/.local/bin/mangohud-gamesir-battery --once
```

Expected output is a percentage such as `99%`. Run only one reader for the
receiver: stop any older battery-reader service before testing or enabling
this addon. To test from the checkout without installing, use
`python3 bin/gamesir-battery.py --once`.

### Device permissions

If opening the device fails with a permission error, the optional rule in
`contrib/70-gamesir-g7-pro-8k.rules` grants the logged-in desktop user access to
this specific receiver. An administrator can install it with:

```sh
sudo install -m 644 contrib/70-gamesir-g7-pro-8k.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
```

Unplug and reconnect the receiver afterward. This grants access to its HID
interfaces, not only battery data. Skip this if existing device rules already
grant access. Run the helper and game as your normal user.

### Start at login

```sh
systemctl --user daemon-reload
systemctl --user enable --now mangohud-gamesir-battery.service
```

Check the current reading:

```sh
~/.local/bin/mangohud-gamesir-battery --status
```

The reader reconnects automatically when the receiver becomes available.
Missing, disconnected or stale readings display `Disconnected`.

## MangoHud configuration

Copy the contents of the generated file
`~/.local/share/mangohud-gamesir-battery/MangoHud.conf.example` into the MangoHud
config used by your game. It contains your actual installation path, for example:

```ini
legacy_layout=0
custom_text=G7 Pro
exec=/home/YOUR_USER/.local/bin/mangohud-gamesir-battery --status
```

Replace `YOUR_USER` if writing this manually. Quote paths containing spaces.
Restart the game after changing its config. Goverlay may overwrite custom
lines when you save settings there.

This is a custom text element, not the built-in `device_battery` element. You
can still use `device_battery=gamepad` for other controllers with kernel battery
support.

### Steam, Proton and Flatpak

Run the reader on the host, outside the game sandbox. The game needs access to
the installed script, Python 3 and the cache file, but does not need access to
the USB device or HID bindings. The default cache file is
`$XDG_CACHE_HOME/MangoHud/gamesir-battery.txt`, or
`~/.cache/MangoHud/gamesir-battery.txt` if `XDG_CACHE_HOME` is unset.

If the game has a different home or cache directory, pass the same explicit
`--output /absolute/shared/path/battery.txt` to the reader and `--status`. For
the service, edit `ExecStart` with `systemctl --user edit --full
mangohud-gamesir-battery.service`, then reload and restart the service. The
shared directory must be accessible inside the game's sandbox.

If Python is unavailable inside the game runtime, MangoHud can read the file:

```ini
custom_text=G7 Pro
exec=cat /absolute/shared/path/battery.txt
```

Using `cat` skips the ten-second stale-file check, so it can display an old
percentage if the reader is killed unexpectedly. Normal service shutdown
writes `Disconnected`.

## Update or uninstall

Update from the checkout:

```sh
git pull --ff-only
python3 install.py
systemctl --user daemon-reload
systemctl --user restart mangohud-gamesir-battery.service
```

To uninstall:

```sh
systemctl --user disable --now mangohud-gamesir-battery.service
python3 install.py --uninstall
systemctl --user daemon-reload
```

Remove the custom MangoHud lines. The installer keeps the cache, `.bak` files
and any manually installed udev rule; remove those separately if unwanted.

## How it works

The receiver gets a 64-byte `0x0f, 0xf2` enhanced-report heartbeat every half
second. The reader takes battery percentage from byte 36 of a 64-byte `0x12`
report, and charging status from byte 35 bit 0. It writes results atomically
and refreshes them once a second. The status command rejects files older than
ten seconds.

The helper writes to the vendor interface, but does not change saved settings,
switch controller modes, detach `xpad`, or claim exclusive access. MangoHud
itself only reads the published result.

See [protocol notes](docs/protocol.md) and [contributing](CONTRIBUTING.md).

## Tests

No controller or third-party Python packages are needed:

```sh
python3 -m unittest discover -s tests -v
```

## Background and credits

This project grew out of [MangoHud issue #2199](https://github.com/flightlessmango/MangoHud/issues/2199)
and [PR #2206](https://github.com/flightlessmango/MangoHud/pull/2206). The MangoHud
maintainer recommended distributing the helper as its own project.

The GameSir report layout was identified using the
[GameSir Linux tools / Deadband project](https://github.com/broroeror/gamesir-linux-tools).
Deadband is not a runtime dependency. [MangoHud](https://github.com/flightlessmango/MangoHud)
is a separate project; this is an unofficial addon.

MIT licensed. See [LICENSE](LICENSE).
