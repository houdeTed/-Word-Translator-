import tkinter as tk
import threading
from typing import Optional


class Overlay:
    def __init__(self):
        self.win: Optional[tk.Toplevel] = None
        self._lock = threading.Lock()

    def show(self, original: str, translation: str, x: int, y: int) -> None:
        def _show():
            with self._lock:
                self._destroy()

                win = tk.Toplevel()
                win.overrideredirect(True)
                win.attributes("-topmost", True)
                win.configure(bg="#2d2d2d")

                # 内容
                fg = "#ffffff"
                bg = "#2d2d2d"

                frame = tk.Frame(win, bg=bg, padx=10, pady=8)
                frame.pack()

                src_label = tk.Label(
                    frame, text=original, bg=bg, fg="#aaaaaa",
                    font=("Microsoft YaHei UI", 10), wraplength=400,
                    justify="left", anchor="w"
                )
                src_label.pack(anchor="w")

                sep = tk.Frame(frame, height=1, bg="#555555")
                sep.pack(fill="x", pady=4)

                dst_label = tk.Label(
                    frame, text=translation, bg=bg, fg=fg,
                    font=("Microsoft YaHei UI", 11), wraplength=400,
                    justify="left", anchor="w"
                )
                dst_label.pack(anchor="w")

                # 关闭：点击任意区域、Esc、失去焦点
                for w in (win, frame, src_label, dst_label, sep):
                    w.bind("<Button-1>", lambda e: self._destroy())
                    w.bind("<ButtonRelease-1>", lambda e: "break")
                win.bind("<Escape>", lambda e: self._destroy())
                win.bind("<FocusOut>", lambda e: self._destroy())

                # 定位在鼠标附近
                win.update_idletasks()
                w = win.winfo_reqwidth()
                h = win.winfo_reqheight()
                screen_w = win.winfo_screenwidth()
                screen_h = win.winfo_screenheight()

                px = min(x + 16, screen_w - w - 4)
                py = min(y + 16, screen_h - h - 4)
                px = max(px, 4)
                py = max(py, 4)

                win.geometry(f"+{px}+{py}")
                win.focus_force()
                self.win = win

        threading.Thread(target=_show, daemon=True).start()

    def _destroy(self) -> None:
        try:
            if self.win:
                self.win.destroy()
        except Exception:
            pass
        finally:
            self.win = None
