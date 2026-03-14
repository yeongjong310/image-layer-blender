from __future__ import annotations

import json
import platform
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from PIL import Image, ImageTk

from merge_image_layer.blender import blend_images, blend_to_image, load_and_prepare

FILETYPES = [
    ("이미지/PDF 파일", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp *.pdf"),
    ("이미지 파일", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
    ("PDF 파일", "*.pdf"),
    ("모든 파일", "*.*"),
]

CONFIG_PATH = Path.home() / ".merge-image-layer" / "config.json"


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def _save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2))


def _open_folder(folder: str) -> None:
    system = platform.system()
    if system == "Darwin":
        subprocess.Popen(["open", folder])
    elif system == "Windows":
        subprocess.Popen(["explorer", folder])
    else:
        subprocess.Popen(["xdg-open", folder])


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("이미지 합성 프로그램")
        self.minsize(500, 650)

        self._img1_path: str | None = None
        self._img2_path: str | None = None
        self._preview_photo: ImageTk.PhotoImage | None = None

        config = _load_config()
        self._save_dir: str = config.get("save_dir", str(Path.home() / "Desktop"))

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        # --- Save folder ---
        fd = ttk.Frame(self)
        fd.pack(fill="x", **pad)
        ttk.Label(fd, text="저장 폴더:").pack(side="left")
        self._dir_lbl = ttk.Label(fd, text=self._save_dir, anchor="w")
        self._dir_lbl.pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(fd, text="폴더 열기", command=self._open_save_dir).pack(
            side="right", padx=2
        )
        ttk.Button(fd, text="변경", command=self._pick_save_dir).pack(
            side="right", padx=2
        )

        # --- Image 1 ---
        f1 = ttk.Frame(self)
        f1.pack(fill="x", **pad)
        ttk.Label(f1, text="이미지 1:").pack(side="left")
        self._lbl1 = ttk.Label(f1, text="(선택 안됨)", width=40, anchor="w")
        self._lbl1.pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(f1, text="찾아보기", command=self._pick_img1).pack(side="right")

        # --- Image 2 ---
        f2 = ttk.Frame(self)
        f2.pack(fill="x", **pad)
        ttk.Label(f2, text="이미지 2:").pack(side="left")
        self._lbl2 = ttk.Label(f2, text="(선택 안됨)", width=40, anchor="w")
        self._lbl2.pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(f2, text="찾아보기", command=self._pick_img2).pack(side="right")

        # --- Output format ---
        ff = ttk.Frame(self)
        ff.pack(fill="x", **pad)
        ttk.Label(ff, text="출력 포맷:").pack(side="left")
        self._fmt_var = tk.StringVar(value="jpg")
        ttk.Radiobutton(ff, text="JPG", variable=self._fmt_var, value="jpg").pack(
            side="left", padx=4
        )
        ttk.Radiobutton(ff, text="PNG", variable=self._fmt_var, value="png").pack(
            side="left", padx=4
        )

        # --- Buttons ---
        fb = ttk.Frame(self)
        fb.pack(fill="x", **pad)
        ttk.Button(fb, text="미리보기 업데이트", command=self._update_preview).pack(
            side="left", padx=4
        )
        ttk.Button(fb, text="저장하기", command=self._save).pack(side="left", padx=4)

        # --- Preview area ---
        self._canvas = tk.Canvas(self, bg="#eeeeee", height=400)
        self._canvas.pack(fill="both", expand=True, **pad)

        # --- Status bar ---
        self._status_var = tk.StringVar(value="준비됨")
        ttk.Label(self, textvariable=self._status_var, relief="sunken", anchor="w").pack(
            fill="x", side="bottom", **pad
        )

    def _pick_img1(self) -> None:
        path = filedialog.askopenfilename(filetypes=FILETYPES)
        if path:
            self._img1_path = path
            self._lbl1.config(text=Path(path).name)
            self._update_preview()

    def _pick_img2(self) -> None:
        path = filedialog.askopenfilename(filetypes=FILETYPES)
        if path:
            self._img2_path = path
            self._lbl2.config(text=Path(path).name)
            self._update_preview()

    def _pick_save_dir(self) -> None:
        folder = filedialog.askdirectory(initialdir=self._save_dir)
        if folder:
            self._save_dir = folder
            self._dir_lbl.config(text=folder)
            _save_config({"save_dir": folder})
            self._status_var.set(f"저장 폴더 변경: {folder}")

    def _open_save_dir(self) -> None:
        if Path(self._save_dir).is_dir():
            _open_folder(self._save_dir)
        else:
            self._status_var.set("저장 폴더가 존재하지 않습니다.")

    def _get_preview_image(self) -> Image.Image | None:
        if self._img1_path and self._img2_path:
            return blend_to_image(self._img1_path, self._img2_path)
        if self._img1_path:
            return load_and_prepare(self._img1_path)
        if self._img2_path:
            return load_and_prepare(self._img2_path)
        return None

    def _update_preview(self) -> None:
        img = self._get_preview_image()
        if img is None:
            self._status_var.set("이미지를 선택해주세요.")
            return

        count = bool(self._img1_path) + bool(self._img2_path)
        self._status_var.set("합성 중..." if count == 2 else "미리보기 로드 중...")
        self.update_idletasks()

        self._canvas.update_idletasks()
        cw = max(self._canvas.winfo_width(), 480)
        ch = max(self._canvas.winfo_height(), 400)
        img.thumbnail((cw, ch), Image.LANCZOS)

        self._preview_photo = ImageTk.PhotoImage(img)
        self._canvas.delete("all")
        self._canvas.create_image(
            cw // 2, ch // 2, anchor="center", image=self._preview_photo
        )
        self._status_var.set("미리보기 완료" if count == 1 else "합성 미리보기 완료")

    def _save(self) -> None:
        if not self._img1_path or not self._img2_path:
            self._status_var.set("저장하려면 이미지 2개를 모두 선택해주세요.")
            return

        fmt = self._fmt_var.get()
        ext = "jpg" if fmt == "jpg" else "png"
        default_ext = f".{ext}"
        filetypes = [("JPEG", "*.jpg")] if fmt == "jpg" else [("PNG", "*.png")]

        path = filedialog.asksaveasfilename(
            initialdir=self._save_dir,
            defaultextension=default_ext,
            filetypes=filetypes,
        )
        if not path:
            return

        # Update save dir if user navigated to a different folder
        new_dir = str(Path(path).parent)
        if new_dir != self._save_dir:
            self._save_dir = new_dir
            self._dir_lbl.config(text=new_dir)
            _save_config({"save_dir": new_dir})

        self._status_var.set("저장 중...")
        self.update_idletasks()

        blend_images(
            self._img1_path,
            self._img2_path,
            path,
            fmt=fmt,
            dpi=300,
        )
        self._status_var.set(f"저장 완료: {path}")


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
