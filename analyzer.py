import colorsys
from typing import List, Tuple, Dict, Any
from PIL import Image, ExifTags


def get_dominant_colors(image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
    if image.mode != 'RGB':
        image = image.convert('RGB')
    img = image.copy()
    img.thumbnail((150, 150))
    quantized = img.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    colors = quantized.getcolors()
    dominant = []
    if colors:
        for count, idx in sorted(colors, reverse=True):
            r = palette[idx * 3]
            g = palette[idx * 3 + 1]
            b = palette[idx * 3 + 2]
            dominant.append((r, g, b))
    return dominant[:num_colors]


def get_brightness(image: Image.Image) -> float:
    if image.mode != 'RGB':
        image = image.convert('RGB')
    pixels = image.getdata()
    total_luminance = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels)
    return total_luminance / (len(pixels) * 255.0)


def get_aspect_ratio(image: Image.Image) -> float:
    width, height = image.size
    return width / height if height else 1.0


def get_exif_data(image: Image.Image) -> Dict[str, Any]:
    exif_data = {}
    try:
        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                exif_data[tag] = value
    except Exception:
        pass
    return exif_data


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)


def get_color_name(r: int, g: int, b: int) -> str:
    h, s, v = rgb_to_hsv(r, g, b)
    if v < 0.2:
        return "preto"
    if v > 0.9 and s < 0.1:
        return "branco"
    if s < 0.15:
        return "cinza"
    h_deg = h * 360
    if h_deg < 15 or h_deg >= 345:
        return "vermelho"
    elif h_deg < 45:
        return "laranja"
    elif h_deg < 75:
        return "amarelo"
    elif h_deg < 165:
        return "verde"
    elif h_deg < 255:
        return "azul"
    elif h_deg < 285:
        return "roxo"
    elif h_deg < 330:
        return "rosa"
    return "vermelho"


def analyze_image(image_path: str) -> Dict[str, Any]:
    with Image.open(image_path) as img:
        width, height = img.size
        dominant_colors = get_dominant_colors(img)
        brightness = get_brightness(img)
        aspect_ratio = get_aspect_ratio(img)
        exif_data = get_exif_data(img)
        color_names = [get_color_name(r, g, b) for r, g, b in dominant_colors]
        if aspect_ratio > 1.3:
            orientation = "horizontal"
        elif aspect_ratio < 0.77:
            orientation = "vertical"
        else:
            orientation = "quadrada"
        if brightness < 0.3:
            brightness_cat = "escura"
        elif brightness > 0.7:
            brightness_cat = "clara"
        else:
            brightness_cat = "media"
        return {
            "width": width,
            "height": height,
            "dominant_colors": dominant_colors,
            "color_names": color_names,
            "brightness": brightness,
            "brightness_category": brightness_cat,
            "aspect_ratio": aspect_ratio,
            "orientation": orientation,
            "exif": exif_data
        }