import tkinter as tk
from tkinter import messagebox
import requests, webbrowser, time, os, json, datetime

# ===== CONFIG =====
RAW_KEYS_URL = "https://raw.githubusercontent.com/kkkkk5234/Kcoinapp/main/Key.txt"
GITHUB_API = "https://api.github.com/repos/kkkkk5234/Kcoinapp/contents/Key.txt"
RAW_KEYWEB_URL = "https://raw.githubusercontent.com/kkkkk5234/Kcoinapp/main/Keyweb.txt"
GITHUB_KEYWEB_API = "https://api.github.com/repos/kkkkk5234/Kcoinapp/contents/Keyweb.txt"
GITHUB_TOKEN = "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"

LINK4M_API = "https://link4m.co/api-shorten/v2"
LINK4M_KEY = "68ee653ab963c96e472dd8c1"

LOCAL_FILE = "key.json"

# ===== UTILS =====
def load_used():
    if os.path.exists(LOCAL_FILE):
        return json.load(open(LOCAL_FILE))
    return {}

def save_used(data):
    json.dump(data, open(LOCAL_FILE, "w"))

def fetch_keys():
    return requests.get(RAW_KEYS_URL).text.splitlines()

def delete_key_from_github(key):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.get(GITHUB_API, headers=headers).json()
    sha = r["sha"]
    content = requests.get(RAW_KEYS_URL).text
    new_content = content.replace(key + "\n", "")

    data = {
        "message": "Remove expired key",
        "content": new_content.encode("utf-8").decode("utf-8"),
        "sha": sha
    }
    requests.put(GITHUB_API, headers=headers, json=data)

# ===== MAIN LOGIC =====
def verify_key(key):
    used = load_used()
    if key in used:
        return False, "Key đã hết hạn"

    if key not in fetch_keys():
        return False, "Key không hợp lệ"

    now = time.time()
    if key.startswith("KEY_FREE"):
        used[key] = now + 7 * 3600
    elif key.startswith("KEY_VIP"):
        used[key] = now + 7 * 86400
    else:
        return False, "Sai định dạng key"

    save_used(used)
    return True, "OK"

def monitor_expire(key, root):
    used = load_used()
    while time.time() < used[key]:
        time.sleep(5)
    messagebox.showwarning("Hết hạn", "Key đã hết hạn")
    delete_key_from_github(key)
    root.destroy()

# ===== UI =====
def start_app():
    key = entry.get().strip()
    ok, msg = verify_key(key)
    if not ok:
        messagebox.showerror("Lỗi", msg)
        return
    messagebox.showinfo("Thành công", "Vào app")
    root.withdraw()
    monitor_expire(key, root)

def get_free_key():
    r = requests.get(LINK4M_API, params={
        "api": LINK4M_KEY,
        "url": "https://kkkkk5234.github.io/Kcoinapp/key.html"
    }).json()

    short_link = r.get("shortenedUrl")
    if not short_link:
        messagebox.showerror("Lỗi", "Không lấy được link")
        return

    keyweb = generate_keyweb()
    upload_keyweb_to_github(keyweb)

    messagebox.showinfo(
        "Key Free",
        f"Link4M:\n{short_link}\n\nKey truy cập:\n{keyweb}"
    )

def upload_keyweb_to_github(key):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # lấy file hiện tại (nếu có)
    r = requests.get(GITHUB_KEYWEB_API, headers=headers)
    if r.status_code == 200:
        data = r.json()
        sha = data["sha"]
        content = base64.b64decode(data["content"]).decode()
        content += f"\n{key}"
    else:
        sha = None
        content = key

    payload = {
        "message": "Add KEY_WEB",
        "content": base64.b64encode(content.encode()).decode(),
    }
    if sha:
        payload["sha"] = sha

    requests.put(GITHUB_KEYWEB_API, headers=headers, json=payload)

def generate_keyweb():
    return "KEY_WEB" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def vip_info():
    messagebox.showinfo("Key VIP", "Mua key vip theo ngày tháng năm\nLiên hệ 0854533557")

root = tk.Tk()
root.title("Nhập Key")

entry = tk.Entry(root, width=30)
entry.pack(pady=10)

tk.Button(root, text="Vào app", command=start_app).pack()
tk.Button(root, text="Key Free", command=get_free_key).pack(pady=5)
tk.Button(root, text="Key VIP", command=vip_info).pack()

root.mainloop()
