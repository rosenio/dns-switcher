## License

This project is licensed under the MIT License - see the [MIT LICENSE](https://github.com/rosenio/dns-switcher/blob/master/LICENSE) file for details.

---

# DNS Switcher

A lightweight, privacy-focused Windows system tray utility that allows you to instantly switch between popular DNS providers (AdGuard, Cloudflare, Google, or Custom configurations) with zero terminal flashing.

## Features

- **System Tray Residency**: Runs quietly in the background without cluttering your taskbar.
- **Modern Encryption Support**: Formatted around native Windows configurations.
- **Custom Input Validation**: Features a custom `IPAddressLineEdit` layout that natively blocks invalid IP sequences.
- **Silent Background Execution**: Bypasses string-shell invocation, suppressing annoying terminal windows from flashing when applying settings.
- **UAC Manifest Bundling**: Compiled executables automatically trigger administrative privileges for hassle-free profile changes.

---

## File Structure

```text
dns-switcher/
├── images/
│   ├── adguard.png
│   ├── cloudflare.png
│   ├── google.png
│   ├── custom.png
│   └── app_icon.png
├── scr/
│   └── dns_switcher/
│       ├── __init__.py
│       └── build.py
├── pyproject.toml
└── uv.lock
```

---

## Getting Started

This project is optimized for **uv**, the fast Python package installer and resolver by Astral.

### Prerequisites

1. Install [uv](https://github.com) on your system.
2. Clone or move into your project root folder.

### Installation

Synchronize the project environment and lock-in dependencies automatically:

```bash
uv sync
```

---

## Usage

### Running in Development

To spin up the system tray utility directly within the development virtual environment, run:

```bash
uv run dns-switcher
```

### Building the Standalone Executable (.exe)

To bundle the application, custom icons, assets, and metadata into a single independent binary file, execute the configured build entry point:

```bash
uv run build
```

#### What happens behind the scenes:
- **Packing**: PyInstaller compresses your assets directory and appends it to the binary file.
- **Output Bundle**: Your ready-to-use standalone executable will be generated at `dist/dns-switcher.exe`.
- **Runtime Extraction**: Upon launching the executable, assets are extracted into a temporary `sys._MEIPASS` folder and automatically wiped cleanly upon application termination.

---

## Dependencies

Controlled and managed entirely via `pyproject.toml`:
- `pyside6` / `qtpy`: Native desktop interface hooks and layout configurations.
- `pyinstaller`: Binary packaging.

