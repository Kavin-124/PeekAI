"""Screen capture utilities with Qt hardware-accelerated grab and mss fallback."""
import base64
import io
from typing import Optional, Tuple
from PIL import Image
from PyQt6.QtCore import QBuffer, QIODevice
from PyQt6.QtWidgets import QApplication


def capture_screen(bbox: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bytes, Image.Image, str]:
    """
    Captures either the full screen or a bounding box.
    
    Args:
        bbox: Optional tuple (left, top, width, height). If None, captures the primary screen.
        
    Returns:
        Tuple of (jpeg_bytes, PIL_image, base64_string)
    """
    # 1. Preferred & Most Reliable Method: Qt QScreen grab
    app = QApplication.instance()
    app_created = False
    if not app:
        app = QApplication([])
        app_created = True

    screen = QApplication.primaryScreen()
    if screen:
        try:
            if bbox is not None:
                left, top, width, height = bbox
                pixmap = screen.grabWindow(0, int(left), int(top), int(width), int(height))
            else:
                pixmap = screen.grabWindow(0)

            if not pixmap.isNull():
                # Save directly to in-memory lossless PNG via QBuffer for crystal-clear text/code OCR
                qbuffer = QBuffer()
                qbuffer.open(QIODevice.OpenModeFlag.WriteOnly)
                pixmap.save(qbuffer, "PNG")
                img_bytes = bytes(qbuffer.data())
                qbuffer.close()

                # Load PIL Image from bytes
                pil_img = Image.open(io.BytesIO(img_bytes))

                # Resize only if ultra high-res (e.g. 4K/8K) to keep upload prompt snappy
                max_dim = 2560
                if pil_img.width > max_dim or pil_img.height > max_dim:
                    pil_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    pil_img.save(buf, format="PNG")
                    img_bytes = buf.getvalue()

                b64_str = base64.b64encode(img_bytes).decode("utf-8")
                return img_bytes, pil_img, b64_str
        except Exception:
            pass

    # 2. Fallback to mss if Qt capture was unavailable
    try:
        import mss
        with mss.mss() as sct:
            if bbox is not None:
                left, top, width, height = bbox
                monitor = {"top": int(top), "left": int(left), "width": int(max(10, width)), "height": int(max(10, height))}
            else:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]

            sct_img = sct.grab(monitor)
            pil_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            buffer = io.BytesIO()
            pil_img.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            b64_str = base64.b64encode(img_bytes).decode("utf-8")
            return img_bytes, pil_img, b64_str
    except Exception as e:
        raise RuntimeError(f"All screen capture methods failed: {str(e)}")
