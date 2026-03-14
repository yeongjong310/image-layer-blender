from pathlib import Path

import fitz
import pytest
from PIL import Image

from merge_image_layer.blender import (
    BLEND_MODES,
    blend_images,
    blend_to_image,
    load_and_prepare,
)


@pytest.fixture()
def red_image(tmp_path: Path) -> Path:
    img = Image.new("RGBA", (100, 80), (255, 0, 0, 255))
    p = tmp_path / "red.png"
    img.save(p)
    return p


@pytest.fixture()
def blue_image(tmp_path: Path) -> Path:
    img = Image.new("RGBA", (120, 100), (0, 0, 255, 255))
    p = tmp_path / "blue.png"
    img.save(p)
    return p


@pytest.fixture()
def sample_pdf(tmp_path: Path) -> Path:
    doc = fitz.open()
    page = doc.new_page(width=200, height=150)
    # Draw a green rectangle filling the page
    page.draw_rect(fitz.Rect(0, 0, 200, 150), color=(0, 1, 0), fill=(0, 1, 0))
    p = tmp_path / "sample.pdf"
    doc.save(str(p))
    doc.close()
    return p


class TestLoadAndPrepare:
    def test_load_png(self, red_image: Path) -> None:
        img = load_and_prepare(red_image)
        assert img.mode == "RGBA"
        assert img.size == (100, 80)

    def test_load_pdf(self, sample_pdf: Path) -> None:
        img = load_and_prepare(sample_pdf)
        assert img.mode == "RGBA"
        assert img.width > 0 and img.height > 0


class TestBlendWithPdf:
    def test_pdf_and_image(
        self, sample_pdf: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.png"
        result = blend_images(sample_pdf, blue_image, out, fmt="png")
        assert result == out
        assert out.exists()
        img = Image.open(out)
        assert img.width > 0

    def test_image_and_pdf(
        self, red_image: Path, sample_pdf: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.jpg"
        result = blend_images(red_image, sample_pdf, out, fmt="jpg")
        assert out.exists()

    def test_two_pdfs(self, sample_pdf: Path, tmp_path: Path) -> None:
        out = tmp_path / "result.png"
        result = blend_images(sample_pdf, sample_pdf, out, fmt="png")
        assert out.exists()


class TestBlendImages:
    def test_output_file_created_jpg(
        self, red_image: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.jpg"
        result = blend_images(red_image, blue_image, out, fmt="jpg")
        assert result == out
        assert out.exists()

    def test_output_file_created_png(
        self, red_image: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.png"
        result = blend_images(red_image, blue_image, out, fmt="png")
        assert result == out
        assert out.exists()

    def test_output_size_matches_larger(
        self, red_image: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.png"
        blend_images(red_image, blue_image, out, fmt="png")
        img = Image.open(out)
        assert img.size == (120, 100)

    def test_dpi_metadata(
        self, red_image: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.png"
        blend_images(red_image, blue_image, out, fmt="png", dpi=300)
        img = Image.open(out)
        dpi = img.info.get("dpi")
        assert dpi is not None
        assert abs(dpi[0] - 300) < 1
        assert abs(dpi[1] - 300) < 1

    def test_alpha_zero_gives_first_image(
        self, red_image: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.png"
        blend_images(red_image, blue_image, out, alpha=0.0, mode="alpha", fmt="png")
        img = Image.open(out).convert("RGBA")
        # Center pixel should be red (from img1)
        r, g, b, a = img.getpixel((50, 40))
        assert r == 255
        assert b == 0

    def test_alpha_one_gives_second_image(
        self, red_image: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.png"
        blend_images(red_image, blue_image, out, alpha=1.0, mode="alpha", fmt="png")
        img = Image.open(out).convert("RGBA")
        r, g, b, a = img.getpixel((50, 40))
        assert r == 0
        assert b == 255

    def test_multiply_mode(
        self, red_image: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "result.png"
        blend_images(red_image, blue_image, out, mode="multiply", fmt="png")
        assert out.exists()

    def test_all_modes_produce_output(
        self, red_image: Path, blue_image: Path, tmp_path: Path
    ) -> None:
        for mode in BLEND_MODES:
            out = tmp_path / f"result_{mode}.png"
            blend_images(red_image, blue_image, out, mode=mode, fmt="png")
            assert out.exists()


class TestBlendToImage:
    def test_returns_pil_image(self, red_image: Path, blue_image: Path) -> None:
        result = blend_to_image(red_image, blue_image, alpha=0.5)
        assert isinstance(result, Image.Image)

    def test_size_matches_larger(self, red_image: Path, blue_image: Path) -> None:
        result = blend_to_image(red_image, blue_image)
        assert result.size == (120, 100)

    def test_multiply_sharp(self, red_image: Path, blue_image: Path) -> None:
        result = blend_to_image(red_image, blue_image, mode="multiply")
        assert result.mode == "RGBA"
