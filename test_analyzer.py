"""Unit tests for analyzer module."""
import pytest
from PIL import Image
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import (
    get_dominant_colors,
    get_brightness,
    get_aspect_ratio,
    get_exif_data,
    rgb_to_hsv,
    get_color_name,
    analyze_image,
)


class TestColorAnalysis:

    def test_rgb_to_hsv_red(self):
        h, s, v = rgb_to_hsv(255, 0, 0)
        assert abs(h - 0.0) < 0.02 or abs(h - 1.0) < 0.02
        assert abs(s - 1.0) < 0.02
        assert abs(v - 1.0) < 0.02

    def test_rgb_to_hsv_green(self):
        h, s, v = rgb_to_hsv(0, 255, 0)
        assert abs(h - 0.333) < 0.02
        assert abs(s - 1.0) < 0.02
        assert abs(v - 1.0) < 0.02

    def test_rgb_to_hsv_blue(self):
        h, s, v = rgb_to_hsv(0, 0, 255)
        assert abs(h - 0.666) < 0.02
        assert abs(s - 1.0) < 0.02
        assert abs(v - 1.0) < 0.02

    def test_get_color_name_red(self):
        assert get_color_name(255, 0, 0) == "vermelho"

    def test_get_color_name_green(self):
        assert get_color_name(0, 255, 0) == "verde"

    def test_get_color_name_blue(self):
        assert get_color_name(0, 0, 255) == "azul"

    def test_get_color_name_black(self):
        assert get_color_name(10, 10, 10) == "preto"

    def test_get_color_name_white(self):
        assert get_color_name(250, 250, 250) == "branco"

    def test_get_color_name_gray(self):
        assert get_color_name(128, 128, 128) == "cinza"


class TestImageAnalysis:

    def create_test_image(self, width: int, height: int, color: tuple = (128, 128, 128)) -> Image.Image:
        return Image.new('RGB', (width, height), color)

    def test_get_aspect_ratio_square(self):
        img = self.create_test_image(100, 100)
        assert get_aspect_ratio(img) == 1.0

    def test_get_aspect_ratio_horizontal(self):
        img = self.create_test_image(200, 100)
        assert get_aspect_ratio(img) == 2.0

    def test_get_aspect_ratio_vertical(self):
        img = self.create_test_image(100, 200)
        assert get_aspect_ratio(img) == 0.5

    def test_get_brightness_black(self):
        img = self.create_test_image(10, 10, (0, 0, 0))
        assert get_brightness(img) == 0.0

    def test_get_brightness_white(self):
        img = self.create_test_image(10, 10, (255, 255, 255))
        assert get_brightness(img) == 1.0

    def test_get_brightness_gray(self):
        img = self.create_test_image(10, 10, (128, 128, 128))
        brightness = get_brightness(img)
        assert 0.4 < brightness < 0.6

    def test_get_dominant_colors_single_color(self):
        img = self.create_test_image(50, 50, (255, 0, 0))
        colors = get_dominant_colors(img, num_colors=3)
        assert len(colors) >= 1
        assert colors[0] == (255, 0, 0)

    def test_get_exif_data_no_exif(self):
        img = self.create_test_image(100, 100)
        exif = get_exif_data(img)
        assert isinstance(exif, dict)


class TestFullAnalysis:
    
    def create_test_image(self, width: int, height: int, color: tuple = (128, 128, 128)) -> Image.Image:
        return Image.new('RGB', (width, height), color)

    def test_analyze_image_returns_dict(self):
        img = self.create_test_image(100, 100, (255, 0, 0))
        # Save to temp file
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name

        try:
            result = analyze_image(temp_path)
            assert isinstance(result, dict)
            assert "width" in result
            assert "height" in result
            assert "dominant_colors" in result
            assert "color_names" in result
            assert "brightness" in result
            assert "brightness_category" in result
            assert "aspect_ratio" in result
            assert "orientation" in result
            assert "exif" in result
        finally:
            os.unlink(temp_path)

    def test_analyze_red_image(self):
        img = self.create_test_image(100, 100, (255, 0, 0))
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name

        try:
            result = analyze_image(temp_path)
            assert "vermelho" in result["color_names"]
            assert result["orientation"] == "quadrada"
        finally:
            os.unlink(temp_path)

    def test_analyze_horizontal_image(self):
        img = self.create_test_image(200, 100, (0, 255, 0))
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name

        try:
            result = analyze_image(temp_path)
            assert result["orientation"] == "horizontal"
            assert result["aspect_ratio"] == 2.0
        finally:
            os.unlink(temp_path)

    def test_analyze_vertical_image(self):
        img = self.create_test_image(100, 200, (0, 0, 255))
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name

        try:
            result = analyze_image(temp_path)
            assert result["orientation"] == "vertical"
            assert result["aspect_ratio"] == 0.5
        finally:
            os.unlink(temp_path)

    def test_analyze_dark_image(self):
        img = self.create_test_image(100, 100, (20, 20, 20))
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name

        try:
            result = analyze_image(temp_path)
            assert result["brightness_category"] == "escura"
        finally:
            os.unlink(temp_path)

    def test_analyze_bright_image(self):
        img = self.create_test_image(100, 100, (240, 240, 240))
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name

        try:
            result = analyze_image(temp_path)
            assert result["brightness_category"] == "clara"
        finally:
            os.unlink(temp_path)