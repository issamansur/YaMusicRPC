__title__ = "yamusicrpc"
__author__ = "issamansur"
__license__ = "MIT"
__copyright__ = "Copyright 2025-present issamansur (EDEXADE, Inc)"
__version__ = "1.0.0"

from . import data, exceptions
from . import models, yandex, discord
from .activity_manager import ActivityManager

__all__ = [
    "data",
    "exceptions",

    "models",
    "yandex",
    "discord",

    "ActivityManager",
]
