#!/usr/bin/env python3
"""Install the addon for the current user; no sudo or dependency downloads."""

import argparse
import os
from pathlib import Path
import shlex
import shutil


ROOT = Path(__file__).resolve().parent
NAME = "mangohud-gamesir-battery"


def systemd_quote(path):
    text = str(path).replace("%", "%%").replace("\\", "\\\\").replace('"', '\\"')
    return '"' + text + '"'


def install(prefix, config, uninstall=False):
    executable = prefix / "bin" / NAME
    example = prefix / "share" / NAME / "MangoHud.conf.example"
    service = config / "systemd" / "user" / f"{NAME}.service"
    targets = (executable, example, service)
    if uninstall:
        for target in targets:
            target.unlink(missing_ok=True)
        print("Removed addon files. The battery cache and any .bak backups were kept.")
        return

    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            # Preserve the previous installed version before updating.
            shutil.copy2(target, target.with_name(target.name + ".bak"))

    shutil.copyfile(ROOT / "bin" / "gamesir-battery.py", executable)
    executable.chmod(0o755)
    template = (ROOT / "contrib" / f"{NAME}.service.in").read_text(encoding="utf-8")
    service.write_text(template.replace("@EXECUTABLE@", systemd_quote(executable)),
                       encoding="utf-8")
    example.write_text("legacy_layout=0\ncustom_text=G7 Pro\nexec=" +
                       shlex.quote(str(executable)) + " --status\n", encoding="utf-8")
    print(f"Installed: {executable}\nService: {service}\nMangoHud config: {example}")
    print("The service is not started automatically. See README.md for setup.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=Path, default=Path.home() / ".local")
    parser.add_argument("--config-home", type=Path,
                        default=Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")))
    parser.add_argument("--uninstall", action="store_true",
                        help="remove installed files after disabling the service")
    args = parser.parse_args()
    install(args.prefix.expanduser().resolve(), args.config_home.expanduser().resolve(),
            args.uninstall)


if __name__ == "__main__":
    main()
