import os
import sys

from PIL import Image, ImageDraw


class ImageLoader:
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """
        Get absolute path to resource, works for dev and for PyInstaller
        """
        try:
            # PyInstaller create own folder, so we get it path
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.join(os.path.dirname(__file__), '..')

        return os.path.join(base_path, relative_path)

    @staticmethod
    def create_image() -> Image:
        image = Image.new("RGB", (64, 64), "black")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        return image

    @staticmethod
    def load_icon() -> Image:
        relative_path: str = os.path.join("resources", "logo.png")

        icon_path = ImageLoader.resource_path(relative_path)

        try:
            return Image.open(icon_path).convert("RGBA")
        except Exception as e:
            print(f"[ImageLoader] Unable to load icon: {e}")
            return ImageLoader.create_image()
