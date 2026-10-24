import os
import sys
import ctypes
import subprocess

from qtpy.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QLineEdit, 
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from qtpy.QtGui import QIcon, QPixmap, QPainter, QColor, QRegularExpressionValidator
from qtpy.QtCore import QRegularExpression

# Define DNS server profiles (Primary, Secondary)
DNS_PROFILES = {
    "AdGuard": ("94.140.14.14", "94.140.15.15"),
    "Cloudflare": ("1.1.1.1", "1.0.0.1"),
    "Google": ("8.8.8.8", "8.8.4.4"),
}

INTERFACE_NAME = None 

def get_asset_path(relative_path):
    """Get the absolute path to an asset, working for both dev mode and PyInstaller."""
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Fallback to local project directory root relative to this file
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        
    return os.path.join(base_path, relative_path)

class IPAddressLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        ip_range = r"(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ip_regex = QRegularExpression(f"^{ip_range}\\.{ip_range}\\.{ip_range}\\.{ip_range}$")
        validator = QRegularExpressionValidator(ip_regex, self)
        self.setValidator(validator)
        self.setPlaceholderText("0.0.0.0")
        self.setInputMask("000.000.000.000;_")

class CustomDNSDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom DNS Setup")
        self.setFixedSize(320, 160)
        
        # Set Custom Dialog Icon
        self.setWindowIcon(QIcon(get_asset_path("images/custom.png")))
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Primary DNS Server:"))
        self.primary_input = IPAddressLineEdit(self)
        self.primary_input.setText("1.1.1.1")
        layout.addWidget(self.primary_input)
        
        layout.addWidget(QLabel("Secondary DNS Server (Optional):"))
        self.secondary_input = IPAddressLineEdit(self)
        self.secondary_input.setText("8.8.8.8")
        layout.addWidget(self.secondary_input)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK", self)
        self.cancel_btn = QPushButton("Cancel", self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.ok_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def validate_and_accept(self):
        primary_raw = self.primary_input.text().strip().replace(" ", "")
        if primary_raw == "...":
            QMessageBox.warning(self, "Validation Error", "The Primary DNS field cannot be empty.")
            return
        self.accept()

    def get_values(self):
        primary = self.primary_input.text().strip().replace(" ", "")
        secondary = self.secondary_input.text().strip().replace(" ", "")
        if secondary == "...":
            secondary = ""
        return primary, secondary

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_active_interface():
    global INTERFACE_NAME
    if INTERFACE_NAME:
        return INTERFACE_NAME
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Get-NetAdapter | Select-Object -ExpandProperty Name"
        ]
        result = run_silent_cmd(cmd).stdout.strip()
        interfaces = [line.strip() for line in result.split('\n') if line.strip()]
        if interfaces:
            return interfaces[0]
    except Exception:
        pass
    return "Wi-Fi"

def run_silent_cmd(cmd_list):
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
    return subprocess.run(cmd_list, startupinfo=startupinfo, capture_output=True, text=True)

def set_dns(profile_name):
    interface = get_active_interface()
    primary = ""
    secondary = ""
    
    if profile_name == "Custom":
        dialog = CustomDNSDialog()
        if dialog.exec_() == QDialog.Accepted:
            primary, secondary = dialog.get_values()
        else:
            return
            
    elif profile_name in DNS_PROFILES:
        primary, secondary = DNS_PROFILES[profile_name]
        
    else:
        run_silent_cmd(["netsh", "interface", "ip", "set", "dns", f"name={interface}", "source=dhcp"])
        run_silent_cmd(["ipconfig", "/flushdns"])
        QMessageBox.information(None, "Success", f"Successfully reset {interface} to Automatic (DHCP).")
        return

    run_silent_cmd(["netsh", "interface", "ip", "set", "dns", f"name={interface}", "source=static", f"addr={primary}", "register=primary"])
    
    if secondary:
        run_silent_cmd(["netsh", "interface", "ip", "add", "dns", f"name={interface}", f"addr={secondary}", "index=2"])
    else:
        run_silent_cmd(["netsh", "interface", "ip", "set", "dns", f"name={interface}", "static", f"addr={primary}"])
        
    run_silent_cmd(["ipconfig", "/flushdns"])
    
    ips_configured = f"{primary}" + (f", {secondary}" if secondary else "")
    QMessageBox.information(
        None, 
        "Success", 
        f"Successfully applied {profile_name} DNS profile to {interface}!\n\nConfigured IPs: {ips_configured}"
    )

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Explicitly configure Windows App User Model ID so the taskbar groups the icon correctly
    myappid = 'rosenio.dnsswitcher.tray.v0.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # Global application icon assignment
    app_icon = QIcon(get_asset_path("images/app_icon.ico"))
    app.setWindowIcon(app_icon)
    
    # Set up the System Tray Icon using app_icon.png
    tray = QSystemTrayIcon(app_icon, app)
    tray.setToolTip("DNS Switcher")
    
    menu = QMenu()
    
    # Add profile actions with bundled icon images
    adguard_action = QAction(QIcon(get_asset_path("images/adguard.png")), "AdGuard DNS", menu)
    adguard_action.triggered.connect(lambda: set_dns("AdGuard"))
    menu.addAction(adguard_action)
    
    cloudflare_action = QAction(QIcon(get_asset_path("images/cloudflare.png")), "Cloudflare DNS", menu)
    cloudflare_action.triggered.connect(lambda: set_dns("Cloudflare"))
    menu.addAction(cloudflare_action)
    
    google_action = QAction(QIcon(get_asset_path("images/google.png")), "Google DNS", menu)
    google_action.triggered.connect(lambda: set_dns("Google"))
    menu.addAction(google_action)
    
    custom_action = QAction(QIcon(get_asset_path("images/custom.png")), "Custom DNS...", menu)
    custom_action.triggered.connect(lambda: set_dns("Custom"))
    menu.addAction(custom_action)
    
    menu.addSeparator()
    
    dhcp_action = QAction("Reset to Automatic (DHCP)", menu)
    dhcp_action.triggered.connect(lambda: set_dns("DHCP"))
    menu.addAction(dhcp_action)
    
    menu.addSeparator()
    
    exit_action = QAction("Exit", menu)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)
    
    tray.setContextMenu(menu)
    tray.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    if is_admin():
        main()
    else:
        print("Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
