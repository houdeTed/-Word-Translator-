import ctypes
import ctypes.wintypes
import threading
import time

MOD_ALT = 0x0001
VK_Z = 0x5A
WM_HOTKEY = 0x0312
HOTKEY_ID = 1

_handler = None
_running = False
DEBOUNCE_SEC = 1.0
_last_trigger = 0.0

# 显式声明 DefWindowProcW 签名（64 位兼容）
ctypes.windll.user32.DefWindowProcW.argtypes = (
    ctypes.wintypes.HWND,
    ctypes.wintypes.UINT,
    ctypes.c_uint64,
    ctypes.c_int64,
)
ctypes.windll.user32.DefWindowProcW.restype = ctypes.c_int64


class _WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", ctypes.wintypes.UINT),
        ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", ctypes.wintypes.HINSTANCE),
        ("hIcon", ctypes.c_void_p),
        ("hCursor", ctypes.c_void_p),
        ("hbrBackground", ctypes.c_void_p),
        ("lpszMenuName", ctypes.wintypes.LPCWSTR),
        ("lpszClassName", ctypes.wintypes.LPCWSTR),
    ]


WndProcType = ctypes.WINFUNCTYPE(
    ctypes.c_int64, ctypes.wintypes.HWND, ctypes.wintypes.UINT,
    ctypes.c_uint64, ctypes.c_int64
)

_wnd_proc_callback = None


def _wnd_proc(hwnd, msg, wParam, lParam):
    global _last_trigger
    if msg == WM_HOTKEY and wParam == HOTKEY_ID:
        now = time.monotonic()
        if now - _last_trigger >= DEBOUNCE_SEC:
            _last_trigger = now
            if _handler:
                threading.Thread(target=_handler, daemon=True).start()
        return 0
    return ctypes.windll.user32.DefWindowProcW(hwnd, msg, wParam, lParam)


def _message_loop():
    global _running, _wnd_proc_callback

    user32 = ctypes.windll.user32
    hinst = ctypes.windll.kernel32.GetModuleHandleW(None)

    _wnd_proc_callback = WndProcType(_wnd_proc)
    wnd_class = _WNDCLASSW()
    wnd_class.lpfnWndProc = ctypes.cast(_wnd_proc_callback, ctypes.c_void_p)
    wnd_class.hInstance = hinst
    wnd_class.lpszClassName = "HotkeyWnd"
    atom = user32.RegisterClassW(ctypes.byref(wnd_class))
    if not atom:
        raise RuntimeError("RegisterClassW failed")

    hwnd = user32.CreateWindowExW(
        0, ctypes.wintypes.LPCWSTR(atom), "HW", 0, 0, 0, 0, 0, None, None, hinst, None
    )
    if not hwnd:
        raise RuntimeError("CreateWindowExW failed")

    if not user32.RegisterHotKey(hwnd, HOTKEY_ID, MOD_ALT, VK_Z):
        err = ctypes.windll.kernel32.GetLastError()
        raise RuntimeError(f"热键注册失败 (error {err})，Alt+Z 可能被其他程序占用")

    _running = True

    msg = ctypes.wintypes.MSG()
    while _running:
        ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
        if ret <= 0:
            break
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    user32.UnregisterHotKey(hwnd, HOTKEY_ID)
    user32.DestroyWindow(hwnd)
    user32.UnregisterClassW(ctypes.wintypes.LPCWSTR(atom), hinst)


def register_hotkey(handler):
    global _handler
    _handler = handler
    threading.Thread(target=_message_loop, daemon=True).start()


def unregister():
    global _running
    _running = False
    hwnd = ctypes.windll.user32.FindWindowW("HotkeyWnd", "HW")
    if hwnd:
        ctypes.windll.user32.PostMessageW(hwnd, 0, 0, 0)
