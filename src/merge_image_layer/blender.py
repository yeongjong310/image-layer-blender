from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image, ImageChops

PDF_DPI = 300

BLEND_MODES = ["multiply", "alpha", "screen", "darken", "lighten"]


def _pdf_to_image(path: str | Path) -> Image.Image:
    doc = fitz.open(str(path))
    page = doc[0]
    mat = fitz.Matrix(PDF_DPI / 72, PDF_DPI / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img.convert("RGBA")


def _is_pdf(path: str | Path) -> bool:
    return Path(path).suffix.lower() == ".pdf"


def _flatten_to_white(img: Image.Image) -> Image.Image:
    """Flatten RGBA image onto white background, then restore full alpha."""
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(white, img)
    return flat


def load_and_prepare(path: str | Path) -> Image.Image:
    if _is_pdf(path):
        return _pdf_to_image(path)
    img = Image.open(path).convert("RGBA")
    return _flatten_to_white(img)


def _match_size(
    img1: Image.Image, img2: Image.Image
) -> tuple[Image.Image, Image.Image, int, int]:
    w = max(img1.width, img2.width)
    h = max(img1.height, img2.height)
    if img1.size != (w, h):
        img1 = img1.resize((w, h), Image.LANCZOS)
    if img2.size != (w, h):
        img2 = img2.resize((w, h), Image.LANCZOS)
    return img1, img2, w, h


def _blend_alpha(img1: Image.Image, img2: Image.Image, alpha: float) -> Image.Image:
    """Alpha blend — weight-based transparency compositing on white canvas."""
    img1, img2, w, h = _match_size(img1, img2)

    layer1 = img1.copy()
    a1 = layer1.getchannel("A").point(lambda v: int(v * (1.0 - alpha)))
    layer1.putalpha(a1)

    layer2 = img2.copy()
    a2 = layer2.getchannel("A").point(lambda v: int(v * alpha))
    layer2.putalpha(a2)

    canvas = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    canvas = Image.alpha_composite(canvas, layer1)
    canvas = Image.alpha_composite(canvas, layer2)
    return canvas


def _blend_multiply(
    img1: Image.Image, img2: Image.Image, _alpha: float
) -> Image.Image:
    """Multiply blend — both layers stay sharp. White passes through."""
    img1, img2, w, h = _match_size(img1, img2)
    rgb1 = img1.convert("RGB")
    rgb2 = img2.convert("RGB")
    result = ImageChops.multiply(rgb1, rgb2)
    return result.convert("RGBA")


def _blend_screen(
    img1: Image.Image, img2: Image.Image, _alpha: float
) -> Image.Image:
    """Screen blend — opposite of multiply. Black passes through."""
    img1, img2, w, h = _match_size(img1, img2)
    rgb1 = img1.convert("RGB")
    rgb2 = img2.convert("RGB")
    result = ImageChops.screen(rgb1, rgb2)
    return result.convert("RGBA")


def _blend_darken(
    img1: Image.Image, img2: Image.Image, _alpha: float
) -> Image.Image:
    """Darken — keeps the darker pixel of each pair."""
    img1, img2, w, h = _match_size(img1, img2)
    rgb1 = img1.convert("RGB")
    rgb2 = img2.convert("RGB")
    result = ImageChops.darker(rgb1, rgb2)
    return result.convert("RGBA")


def _blend_lighten(
    img1: Image.Image, img2: Image.Image, _alpha: float
) -> Image.Image:
    """Lighten — keeps the lighter pixel of each pair."""
    img1, img2, w, h = _match_size(img1, img2)
    rgb1 = img1.convert("RGB")
    rgb2 = img2.convert("RGB")
    result = ImageChops.lighter(rgb1, rgb2)
    return result.convert("RGBA")


_BLEND_FNS = {
    "multiply": _blend_multiply,
    "alpha": _blend_alpha,
    "screen": _blend_screen,
    "darken": _blend_darken,
    "lighten": _blend_lighten,
}


def composite(
    img1: Image.Image,
    img2: Image.Image,
    alpha: float = 0.5,
    mode: str = "multiply",
) -> Image.Image:
    fn = _BLEND_FNS.get(mode, _blend_multiply)
    return fn(img1, img2, alpha)


def blend_images(
    img1_path: str | Path,
    img2_path: str | Path,
    output_path: str | Path,
    *,
    alpha: float = 0.5,
    mode: str = "multiply",
    fmt: str = "jpg",
    dpi: int = 300,
) -> Path:
    output_path = Path(output_path)
    img1 = load_and_prepare(img1_path)
    img2 = load_and_prepare(img2_path)

    blended = composite(img1, img2, alpha, mode)

    fmt_lower = fmt.lower()
    save_kwargs: dict = {"dpi": (dpi, dpi)}

    if fmt_lower in ("jpg", "jpeg"):
        out = blended.convert("RGB")
        save_kwargs["quality"] = 100
        save_kwargs["subsampling"] = 0
        out.save(output_path, format="JPEG", **save_kwargs)
    else:
        blended.save(output_path, format="PNG", **save_kwargs)

    return output_path


def blend_to_image(
    img1_path: str | Path,
    img2_path: str | Path,
    *,
    alpha: float = 0.5,
    mode: str = "multiply",
) -> Image.Image:
    img1 = load_and_prepare(img1_path)
    img2 = load_and_prepare(img2_path)
    return composite(img1, img2, alpha, mode)
