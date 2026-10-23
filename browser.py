import sys
import os
import json
from pathlib import Path
from PyQt6.QtCore import Qt, QUrl, QStandardPaths
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, 
                             QLineEdit, QPushButton, QComboBox, 
                             QVBoxLayout, QWidget, QProgressBar,
                             QDialog, QFormLayout, QCheckBox, QDialogButtonBox, 
                             QLabel, QMessageBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (QWebEngineProfile, QWebEngineSettings, 
                                   QWebEngineGlobalSettings, QWebEngineUrlRequestInterceptor,
                                   QWebEnginePage)
from PyQt6.QtNetwork import QNetworkProxy

CONFIG_DIR = Path.home() / ".config"
CONFIG_FILE = CONFIG_DIR / "zenbrowser.json"

THEMES = {
    "Catppuccin (Dark)": """
        QMainWindow, QWidget, QDialog { background-color: #1e1e2e; color: #cdd6f4; }
        QToolBar { background-color: #181825; border: none; padding: 8px; spacing: 10px; }
        QLineEdit { background-color: #313244; border: 1px solid #45475a; border-radius: 16px; padding: 8px 16px; color: #cdd6f4; font-size: 14px; }
        QLineEdit:focus { border: 1px solid #89b4fa; }
        QPushButton { background-color: #313244; border: none; border-radius: 16px; padding: 8px 16px; color: #cdd6f4; font-weight: bold; font-size: 14px; }
        QPushButton:hover { background-color: #45475a; }
        QPushButton:pressed { background-color: #585b70; }
        QComboBox { background-color: #313244; border: 1px solid #45475a; border-radius: 16px; padding: 8px 16px; color: #cdd6f4; font-size: 14px; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; selection-background-color: #89b4fa; selection-color: #1e1e2e; border-radius: 8px; }
        QProgressBar { border: none; background-color: #181825; height: 4px; }
        QProgressBar::chunk { background-color: #89b4fa; border-radius: 2px; }
        QCheckBox { spacing: 10px; font-size: 14px; }
        QLabel { font-size: 14px; }
    """,
    "Light (Clean)": """
        QMainWindow, QWidget, QDialog { background-color: #f8f9fa; color: #212529; }
        QToolBar { background-color: #ffffff; border-bottom: 1px solid #e9ecef; border: none; padding: 8px; spacing: 10px; }
        QLineEdit { background-color: #f1f3f5; border: 1px solid #dee2e6; border-radius: 16px; padding: 8px 16px; color: #212529; font-size: 14px; }
        QLineEdit:focus { border: 1px solid #0d6efd; background-color: #ffffff; }
        QPushButton { background-color: #f1f3f5; border: 1px solid #dee2e6; border-radius: 16px; padding: 8px 16px; color: #212529; font-weight: bold; font-size: 14px; }
        QPushButton:hover { background-color: #e9ecef; }
        QPushButton:pressed { background-color: #dee2e6; }
        QComboBox { background-color: #f1f3f5; border: 1px solid #dee2e6; border-radius: 16px; padding: 8px 16px; color: #212529; font-size: 14px; }
        QComboBox QAbstractItemView { background-color: #ffffff; color: #212529; selection-background-color: #0d6efd; selection-color: #ffffff; }
        QProgressBar { border: none; background-color: #e9ecef; height: 4px; }
        QProgressBar::chunk { background-color: #0d6efd; border-radius: 2px; }
        QCheckBox { spacing: 10px; font-size: 14px; }
        QLabel { font-size: 14px; }
    """
}

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, block_list, parent=None):
        super().__init__(parent)
        self.block_list = block_list

    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        for block in self.block_list:
            if block in url:
                info.block(True)
                return

def load_config():
    default_config = {
        "theme": "Catppuccin (Dark)",
        "search_engine": "DuckDuckGo",
        "home_url": "https://www.google.com",
        "adblock_enabled": True,
        "proxy_enabled": False,
        "proxy_host": "127.0.0.1",
        "proxy_port": 1080,
        "doh_enabled": True
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**default_config, **json.load(f)}
        except Exception:
            pass
    return default_config

def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setFixedSize(450, 450)
        
        layout = QFormLayout(self)
        
        self.cb_adblock = QCheckBox("Включить блокировку рекламы (простой список)")
        self.cb_adblock.setChecked(current_settings.get("adblock_enabled", True))
        
        self.cb_doh = QCheckBox("Использовать DNS-over-HTTPS (Cloudflare)")
        self.cb_doh.setChecked(current_settings.get("doh_enabled", True))
        
        self.cb_proxy = QCheckBox("Использовать SOCKS5 прокси")
        self.cb_proxy.setChecked(current_settings.get("proxy_enabled", False))
        self.proxy_host = QLineEdit(current_settings.get("proxy_host", "127.0.0.1"))
        self.proxy_port = QLineEdit(str(current_settings.get("proxy_port", 1080)))
        
        self.search_combo = QComboBox()
        self.search_combo.addItems(["DuckDuckGo", "Google", "Yandex", "Bing"])
        self.search_combo.setCurrentText(current_settings.get("search_engine", "DuckDuckGo"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.setCurrentText(current_settings.get("theme", "Catppuccin (Dark)"))
        
        self.home_input = QLineEdit(current_settings.get("home_url", "https://www.google.com"))
        
        layout.addRow(QLabel("<b>Приватность</b>"))
        layout.addRow(self.cb_adblock)
        layout.addRow(self.cb_doh)
        layout.addRow(QLabel("<b>Сеть (Прокси)</b>"))
        layout.addRow(self.cb_proxy)
        layout.addRow("Host:", self.proxy_host)
        layout.addRow("Port:", self.proxy_port)
        layout.addRow(QLabel("<b>Поиск</b>"))
        layout.addRow("Поисковик:", self.search_combo)
        layout.addRow("Главная:", self.home_input)
        layout.addRow(QLabel("<b>Внешний вид</b>"))
        layout.addRow("Тема:", self.theme_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kody Browser")
        self.resize(1280, 800)
        self.config = load_config()
        
        if self.config.get("doh_enabled", True):
            try:
                dns_mode = QWebEngineGlobalSettings.DnsMode()
                dns_mode.secureMode = QWebEngineGlobalSettings.SecureDnsMode.SecureWithFallback
                dns_mode.serverTemplates = ["https://1.1.1.1/dns-query{?dns}"]
                QWebEngineGlobalSettings.setDnsMode(dns_mode)
            except Exception as e:
                print(f"DoH setup failed: {e}")

        self.profile = QWebEngineProfile("ZenBrowserProfile", self)
        
        data_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        os.makedirs(data_path, exist_ok=True)
        self.profile.setPersistentStoragePath(os.path.join(data_path, "storage"))
        
        cache_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
        os.makedirs(cache_path, exist_ok=True)
        self.profile.setCachePath(os.path.join(cache_path, "cache"))
        
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        
        if self.config.get("adblock_enabled", True):
            block_list = [
                "doubleclick.net", "google-analytics.com", "googletagmanager.com",
                "facebook.net", "adservice.google.com", "ads.yahoo.com"
            ]
            self.interceptor = AdBlockInterceptor(block_list, self)
            self.profile.setUrlRequestInterceptor(self.interceptor)

        if self.config.get("proxy_enabled", False):
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.ProxyType.Socks5Proxy)
            proxy.setHostName(self.config.get("proxy_host", "127.0.0.1"))
            proxy.setPort(int(self.config.get("proxy_port", 1080)))
            QNetworkProxy.setApplicationProxy(proxy)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setToolTip("Настройки")
        self.btn_settings.clicked.connect(self.open_settings)

        self.btn_home = QPushButton("⌂")
        self.btn_home.setToolTip("Главная")
        self.btn_home.clicked.connect(self.go_home)

        self.btn_back = QPushButton("←")
        self.btn_back.clicked.connect(lambda: self.webview.back())
        
        self.btn_forward = QPushButton("→")
        self.btn_forward.clicked.connect(lambda: self.webview.forward())
        
        self.btn_reload = QPushButton("↻")
        self.btn_reload.clicked.connect(lambda: self.webview.reload())

        self.search_combo = QComboBox()
        self.search_combo.addItems(["DuckDuckGo", "Google", "Yandex", "Bing"])
        self.search_combo.setFixedWidth(130)
        self.search_combo.setCurrentText(self.config["search_engine"])

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL или поисковый запрос...")
        self.url_bar.returnPressed.connect(self.navigate)

        self.toolbar.addWidget(self.btn_settings)
        self.toolbar.addWidget(self.btn_home)
        self.toolbar.addWidget(self.btn_back)
        self.toolbar.addWidget(self.btn_forward)
        self.toolbar.addWidget(self.btn_reload)
        self.toolbar.addWidget(self.search_combo)
        self.toolbar.addWidget(self.url_bar)

        self.webview = QWebEngineView()
        
        page = QWebEnginePage(self.profile, self.webview)
        self.webview.setPage(page)
        
        self.webview.setUrl(QUrl(self.config["home_url"]))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        self.webview.loadStarted.connect(lambda: (self.progress_bar.show(), self.progress_bar.setValue(0)))
        self.webview.loadProgress.connect(self.progress_bar.setValue)
        self.webview.loadFinished.connect(lambda _: self.progress_bar.hide())
        self.webview.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()))

        layout.addWidget(self.toolbar)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.webview)
        self.setCentralWidget(central_widget)
        self.setStyleSheet(THEMES[self.config["theme"]])

    def navigate(self):
        text = self.url_bar.text().strip()
        if not text: return
        if "." in text and " " not in text:
            if not text.startswith("http"):
                text = "https://" + text
            url = text
        else:
            engines = {
                "DuckDuckGo": "https://duckduckgo.com/?q={}",
                "Google": "https://www.google.com/search?q={}",
                "Yandex": "https://yandex.ru/search/?text={}",
                "Bing": "https://www.bing.com/search?q={}"
            }
            url = engines[self.search_combo.currentText()].format(text)
        self.webview.setUrl(QUrl(url))

    def go_home(self):
        self.webview.setUrl(QUrl(self.config["home_url"]))

    def open_settings(self):
        dialog = SettingsDialog(self, self.config)
        if dialog.exec():
            self.config.update({
                "adblock_enabled": dialog.cb_adblock.isChecked(),
                "doh_enabled": dialog.cb_doh.isChecked(),
                "proxy_enabled": dialog.cb_proxy.isChecked(),
                "proxy_host": dialog.proxy_host.text(),
                "proxy_port": int(dialog.proxy_port.text() or 1080),
                "search_engine": dialog.search_combo.currentText(),
                "theme": dialog.theme_combo.currentText(),
                "home_url": dialog.home_input.text()
            })
            save_config(self.config)
            QMessageBox.information(self, "Настройки", 
                "Некоторые настройки (DoH, прокси, AdBlock) требуют перезапуска браузера.\n"
                "Куки и данные сайтов сохраняются в:\n"
                f"{QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec())
