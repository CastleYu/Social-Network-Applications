import json
import threading
import tkinter as tk
from io import BytesIO

import requests
from PIL import Image, ImageTk
from lxml import etree


def save_cookie_to_file(cookie_dict, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(cookie_dict, file, indent=4, ensure_ascii=False)


def read_cookie_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            cookie_dict = json.load(file)
            return cookie_dict
    except FileNotFoundError:
        return None


def save_element_content_to_file(element, file_path):
    content = etree.tostring(element, pretty_print=True, encoding='utf-8')
    if not file_path.endswith('.html'):
        file_path += '.html'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
        file.close()


def show_image_by_url(image_url, event: threading.Event):
    # 下载图像
    try:
        response = requests.get(image_url)
    except:
        print("Error when downloading image")
        return None
    image_bytes = BytesIO(response.content)
    image = Image.open(image_bytes)

    # 使用Tkinter显示图像
    def run_gui(e):
        root = tk.Tk()
        root.title("Scan the QR Code to Login")
        tk_image = ImageTk.PhotoImage(image)
        tk.Label(root, image=tk_image).pack()

        # 将窗口置顶
        root.attributes('-topmost', 1)

        # 检查事件是否已设置，并据此关闭窗口
        def check_event():
            if e.is_set():
                root.destroy()
            else:
                root.after(100, check_event)

        # 启动检查事件的循环
        check_event()

        root.mainloop()

    # 在新线程中运行GUI
    gui_thread = threading.Thread(target=run_gui, args=(event,))
    gui_thread.start()
