import configparser
import os

from dotenv import load_dotenv


class Config:
    def __init__(self, config_file="config.ini", env_file=".env"):
        # Load environment variables
        load_dotenv(env_file)

        self.config = configparser.ConfigParser()
        self.config.read(os.path.abspath(config_file))

        # App Information
        self.APP_NAME = self.get_config("APP", "APP_NAME")
        self.VERSION = self.get_config("APP", "VERSION")

        # Window Settings
        self.WINDOW_PAD_X = int(self.get_config("WINDOW", "WINDOW_PAD_X"))
        self.WINDOW_PAD_Y = int(self.get_config("WINDOW", "WINDOW_PAD_Y"))
        self.CANVAS_WIDTH = int(self.get_config("WINDOW", "CANVAS_WIDTH"))
        self.CANVAS_HEIGHT = int(self.get_config("WINDOW", "CANVAS_HEIGHT"))
        self.PAD_X = int(self.get_config("WINDOW", "PAD_X"))
        self.PAD_Y = int(self.get_config("WINDOW", "PAD_Y"))

        # Colors
        self.BACKGROUND_COLOR = self.get_config("COLORS", "BACKGROUND_COLOR")
        self.BACKGROUND_COLOR_2 = self.get_config("COLORS", "BACKGROUND_COLOR_2")

        # Asset Directories
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ASSETS_DIR = os.path.join(self.BASE_DIR, self.get_config("ASSETS", "ASSETS_DIR"))
        self.FONT_DIR = os.path.join(self.BASE_DIR, self.get_config("ASSETS", "FONT_DIR"))
        self.IMAGE_DIR = os.path.join(self.BASE_DIR, self.get_config("ASSETS", "IMAGE_DIR"))

        # Image Processing Settings
        self.IMAGE_FORMATS = tuple(self.get_config("IMAGE_PROCESSING", "IMAGE_FORMATS").split(", "))
        self.THUMBNAIL_SIZE = tuple(map(int, self.get_config("IMAGE_PROCESSING", "THUMBNAIL_SIZE").split(", ")))

        # Defaults
        self.DEFAULT_FONT = self.get_config("DEFAULTS", "DEFAULT_FONT")
        self.DEFAULT_FONT_SIZE = int(self.get_config("DEFAULTS", "DEFAULT_FONT_SIZE"))
        self.DEFAULT_FONT_STYLE = self.get_config("DEFAULTS", "DEFAULT_FONT_STYLE")
        self.DEFAULT_FONT_COLOR_RGB = tuple(map(int, self.get_config("DEFAULTS", "DEFAULT_FONT_COLOR_RGB").split(", ")))
        self.DEFAULT_FONT_COLOR_HEX = self.get_config("DEFAULTS", "DEFAULT_FONT_COLOR_HEX")
        self.DEFAULT_WATERMARK = self.get_config("DEFAULTS", "DEFAULT_WATERMARK")
        self.DEFAULT_OPACITY = int(self.get_config("DEFAULTS", "DEFAULT_OPACITY"))

        # Text Settings
        self.INITIAL_POSITION = tuple(map(int, self.get_config("TEXT", "INITIAL_POSITION").split(", ")))
        self.TEXT_ANCHOR = self.get_config("TEXT", "TEXT_ANCHOR")

        # Logging (Uses Environment Variables)
        self.LOG_FILE = os.getenv("LOG_FILE", os.path.join(self.BASE_DIR, self.get_config("LOGGING", "LOG_FILE")))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.get_config("LOGGING", "LOG_LEVEL"))

    def get_config(self, section, key, default=None):
        """Helper function to get a config value with a fallback."""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def get_image_path(self, image_name):
        """Get full path of an image file."""
        return os.path.join(self.IMAGE_DIR, image_name)


# Initialize Config object
config = Config(config_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))
