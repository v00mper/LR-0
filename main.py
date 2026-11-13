import ctypes
from ctypes import wintypes
import msvcrt
import shutil
import sys
import time


def main():
    console = ctypes.WinDLL("kernel32", use_last_error=True)
    console.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    console.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    handle = msvcrt.get_osfhandle(sys.stdout.fileno())
    old_mode = wintypes.DWORD()
    if not console.GetConsoleMode(handle, ctypes.byref(old_mode)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not console.SetConsoleMode(handle, old_mode.value | 5):
        raise ctypes.WinError(ctypes.get_last_error())

    columns, rows = shutil.get_terminal_size()
    x, y = columns // 2, rows // 2
    dx = dy = 1
    speed = 1

    try:
        # Сохраняем курсор и переключаемся на отдельный экран для анимации.
        print("\x1b7\x1b[?1049h", end="", flush=True)
        while True:
            columns, rows = shutil.get_terminal_size()
            width, height = columns-1, rows-1
            x, y = min(x, width - 1), min(y, height - 1)

            if msvcrt.kbhit():
                key = msvcrt.getwch()
                if key in ("\x00", "\xe0"):
                    msvcrt.getwch()
                elif key.lower() == "q":
                    break
                elif key in ("+", "="):
                    speed = min(speed + 1, 4)
                elif key == "-":
                    speed = max(speed - 1, 1)
                elif key == " ":
                    x, y = width // 2, height // 2
                    dx = dy = 1
                    speed = 1

            print("\x1b[H\x1b[2J", end="")
            print(f"Speed: {speed}x | +/- | Space: reset | Q: exit"[:width])
            print("\n" * y + " " * x + "*", end="", flush=True)
            time.sleep(0.1 / speed)

            if x + dx < 0 or x + dx >= width:
                dx = -dx
            if y + dy < 0 or y + dy >= height:
                dy = -dy
            x = max(0, min(x + dx, width - 1))
            y = max(0, min(y + dy, height - 1))
    except KeyboardInterrupt:
        pass
    finally:
        try:
            print("\x1b[?1049l\x1b8", end="", flush=True)
        finally:
            console.SetConsoleMode(handle, old_mode.value)


if __name__ == "__main__":
    main()
