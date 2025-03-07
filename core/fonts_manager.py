import os.path
from pathlib import Path

from PIL import ImageFont

from config import config


class FontsManager:
    def __init__(self, fonts_dir=config.FONT_DIR):
        self.fonts_dir = Path(fonts_dir).resolve()
        self.fonts = {}
        self.italic_fonts = {}
        self.font_sizes = list(range(10, 72, 1))
        self.style_mapping = {"bold": "Bold", "italic": "Italic", "normal": "Regular"}
        self._init_fonts()

    def _init_fonts(self):
        if not self.fonts_dir.exists():
            raise FileNotFoundError(f"Fonts directory '{self.fonts_dir}' does not exist.")

        for font_dir in self.fonts_dir.iterdir():
            if not font_dir.is_dir():
                continue

            for font_file in list(font_dir.glob("*.ttf")):
                if "Italic" in font_file.stem:
                    self.italic_fonts[font_dir.name] = font_file
                else:
                    self.fonts[font_dir.name] = font_file

    def get_font(self, name, size, style="normal"):
        if name not in self.fonts and name not in self.italic_fonts:
            raise ValueError(f"Font '{name}' not found.")

        style_name = self.style_mapping.get(style, "Regular")
        font_path = self.italic_fonts.get(name) if style_name == "Italic" else self.fonts.get(name)

        if not font_path:
            raise ValueError(f"Font style '{style}' not available for '{name}'.")

        font = ImageFont.truetype(str(font_path), size, layout_engine=ImageFont.Layout.BASIC)
        font.set_variation_by_name(style_name)

        return font

    def get_all_fonts(self):
        return list(self.fonts.keys())

    def get_available_styles(self):
        return list(self.style_mapping.keys())
