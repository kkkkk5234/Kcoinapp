import sys, requests, datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt, QTimer

# ================= CONFIG =================

LINK4M_API = "https://link4m.co/api-shorten/v2"
LINK4M_API_KEY = "68ee653ab963c96e472dd8c1"

TARGET_KEY_WEB = "https://kkkkk5234.github.io/Kcoinapp/key.html"
GITHUB_KEY_RAW = "https://raw.githubusercontent.com/kkkkk5234/Kcoinapp/main/Key.txt"
MAIN_WEB = "https://kkkkk5234.github.io/Kcoinapp/main.html"

KEY_DOMAIN = "https://kkkkk5234.github.io/Kcoinapp/key.html"
KEY_ELEMENT_ID = "key"
KEY_QUERY_NAME = "key"

# ================= UTILS =================

def get_link4m():
    api = f"{LINK4M_API}?api={LINK4M_API_KEY}&url={TARGET_KEY_WEB}"
    r = requests.get(api, timeout=10)
    return r.json().get("shortenedUrl")

def check_key(key):
    today = str(datetime.date.today())
    raw = requests.get(GITHUB_KEY_RAW, timeout=10).text

    for line in raw.splitlines():
        try:
            k, date = line.split("|")
            if k == key and date >= today:
                return True
        except:
            pass
    return False

# ================= APP =================

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kcoin App")
        self.resize(420, 220)

        layout = QVBoxLayout(self)

        self.label = QLabel("Nhập key để mở app")
        self.input = QLineEdit()
        self.input.setPlaceholderText("Nhập key tại đây")

        self.btn_check = QPushButton("Xác nhận key")
        self.btn_free = QPushButton("Key Free")
        self.btn_vip = QPushButton("Key VIP")

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.btn_check)
        layout.addWidget(self.btn_free)
        layout.addWidget(self.btn_vip)

        self.btn_free.clicked.connect(self.open_key_free)
        self.btn_vip.clicked.connect(self.vip_info)
        self.btn_check.clicked.connect(self.verify_key)

        self.setStyleSheet("""
        QWidget { background:#121212; color:white; font-size:14px; }
        QLineEdit { padding:10px; border-radius:10px; background:#1f1f1f; }
        QPushButton { padding:10px; border-radius:10px; background:#2979ff; }
        QPushButton:hover { background:#448aff; }
        """)

    # ================= KEY FREE =================

    def open_key_free(self):
        link = get_link4m()
        if not link:
            QMessageBox.warning(self, "Lỗi", "Không lấy được link")
            return

        self.web = QWebEngineView()
        self.web.setContextMenuPolicy(Qt.NoContextMenu)
        self.web.settings().setAttribute(
            self.web.settings().DeveloperExtrasEnabled, False
        )

        self.web.urlChanged.connect(self.on_url_change)
        self.web.load(QUrl(link))
        self.web.show()
        self.hide()

    def on_url_change(self, url: QUrl):
        url_str = url.toString()

        if f"{KEY_QUERY_NAME}=" in url_str:
            query = QUrl(url_str).query()
            params = dict(x.split("=") for x in query.split("&") if "=" in x)
            self.finish_get_key(params.get(KEY_QUERY_NAME, ""))
            return

        if KEY_DOMAIN in url_str:
            self.start_js_polling()

    def start_js_polling(self):
        if hasattr(self, "key_timer"):
            return
        self.key_timer = QTimer(self)
        self.key_timer.timeout.connect(self.poll_key_from_dom)
        self.key_timer.start(500)

    def poll_key_from_dom(self):
        js = f"""
        (function() {{
            let el = document.getElementById("{KEY_ELEMENT_ID}");
            if (el) return el.innerText || el.value;
            return "";
        }})();
        """
        self.web.page().runJavaScript(js, self.on_js_key_result)

    def on_js_key_result(self, key):
        if key and len(key) > 3:
            self.key_timer.stop()
            self.finish_get_key(key)

    def finish_get_key(self, key):
        if key:
            self.web.close()
            self.input.setText(key.strip())
            self.show()

    # ================= CHECK KEY =================

    def verify_key(self):
        if check_key(self.input.text().strip()):
            self.open_main()
        else:
            QMessageBox.warning(self, "Sai key", "Key không hợp lệ hoặc đã hết hạn")

    # ================= MAIN WEB =================

    def open_main(self):
        self.main = QWebEngineView()
        self.main.setContextMenuPolicy(Qt.NoContextMenu)
        self.main.settings().setAttribute(
            self.main.settings().DeveloperExtrasEnabled, False
        )
        self.main.load(QUrl(MAIN_WEB))
        self.main.show()
        self.close()

    def vip_info(self):
        QMessageBox.information(self, "Key VIP",
            "Mua key vip liên hệ 0854533557"
        )

# ================= RUN =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())