import win32api
import tkinter as tk

from translator import translate
from clipboard import copy_selection_and_read
from overlay import Overlay
from hotkey import register_hotkey, unregister

overlay = Overlay()


def on_hotkey() -> None:
    text = copy_selection_and_read()
    if not text:
        return

    translated = translate(text)
    if not translated:
        return

    x, y = win32api.GetCursorPos()
    overlay.show(text, translated, x, y)


def main() -> None:
    # 必须创建 tk 根窗口（隐藏）才能创建 Toplevel
    root = tk.Tk()
    root.withdraw()

    register_hotkey(on_hotkey)
    print("划词翻译器已启动，按 Alt+Z 翻译选中文本")

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        unregister()


if __name__ == "__main__":
    main()
