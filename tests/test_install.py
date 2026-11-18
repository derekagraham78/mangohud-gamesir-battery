import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def test_installs_executable_service_and_config_in_custom_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "local with spaces"
            config = Path(directory) / "config"
            installer.install(prefix, config)
            executable = prefix / "bin" / installer.NAME
            self.assertTrue(executable.stat().st_mode & 0o111)
            self.assertEqual(executable.read_bytes(),
                             (ROOT / "bin" / "gamesir-battery.py").read_bytes())
            service = config / "systemd/user/mangohud-gamesir-battery.service"
            self.assertIn(f'ExecStart="{executable}"', service.read_text())
            example = prefix / "share" / installer.NAME / "MangoHud.conf.example"
            self.assertIn(f"exec='{executable}' --status", example.read_text())
            result = subprocess.run([str(executable), "--status", "--output",
                                     str(Path(directory) / "missing.txt")],
                                    check=True, capture_output=True, text=True)
            self.assertEqual(result.stdout.strip(), "Disconnected")

    def test_update_keeps_backup_and_uninstall_keeps_unrelated_files(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "local"
            config = Path(directory) / "config"
            installer.install(prefix, config)
            executable = prefix / "bin" / installer.NAME
            executable.write_text("previous version")
            unrelated = prefix / "bin" / "unrelated"
            unrelated.write_text("keep me")
            installer.install(prefix, config)
            backup = executable.with_name(executable.name + ".bak")
            self.assertEqual(backup.read_text(), "previous version")
            installer.install(prefix, config, uninstall=True)
            self.assertFalse(executable.exists())
            self.assertFalse((config / "systemd/user/mangohud-gamesir-battery.service").exists())
            self.assertTrue(backup.exists())
            self.assertEqual(unrelated.read_text(), "keep me")

    def test_systemd_path_quoting(self):
        self.assertEqual(installer.systemd_quote(Path('/tmp/a% "b\\c')),
                         '"/tmp/a%% \\"b\\\\c"')

    def test_installer_cli_accepts_staging_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, str(ROOT / "install.py"),
                       "--prefix", str(Path(directory) / "prefix"),
                       "--config-home", str(Path(directory) / "config")]
            subprocess.run(command, check=True, capture_output=True)
            subprocess.run(command + ["--uninstall"], check=True, capture_output=True)
            self.assertFalse((Path(directory) / "prefix/bin" / installer.NAME).exists())


if __name__ == "__main__":
    unittest.main()
