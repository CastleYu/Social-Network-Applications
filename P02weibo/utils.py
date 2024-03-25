import threading
import tkinter as tk
from io import BytesIO

import requests
from PIL import Image, ImageTk


def show_image_by_url(image_url):
    # 下载图像
    response = requests.get(image_url)
    image_bytes = BytesIO(response.content)
    image = Image.open(image_bytes)

    # 使用Tkinter显示图像
    def run_gui():
        root = tk.Tk()
        root.title("Image on Top")
        tk_image = ImageTk.PhotoImage(image)
        tk.Label(root, image=tk_image).pack()

        # 将窗口置顶
        root.attributes('-topmost', 1)
        root.mainloop()

    # 在新线程中运行GUI
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.start()


# 示例用法
