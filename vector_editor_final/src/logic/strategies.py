from abc import ABC, abstractmethod
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import QRectF, Qt
from src.logic.file_manager import FileManager


class SaveStrategy(ABC):
    @abstractmethod
    def save(self, filename: str, scene):
        pass


class JsonSaveStrategy(SaveStrategy):
    def save(self, filename: str, scene):
        project_data = {
            "meta": {
                "version": "1.0",
                "app": "PyVectorEditor"
            },
            "scene": {
                "width": scene.width(),
                "height": scene.height()
            },
            "shapes": []
        }

        items = list(reversed(scene.items()))

        for item in items:
            if hasattr(item, "to_dict") and item.parentItem() is None:
                try:
                    project_data["shapes"].append(item.to_dict())
                except Exception as e:
                    print(f"Skipping item: {e}")

        FileManager.save_project(filename, project_data)


class ImageSaveStrategy(SaveStrategy):
    def __init__(self, fmt="PNG", bg_color="transparent"):
        self.fmt = fmt
        self.bg_color = bg_color

    def save(self, filename: str, scene):
        rect = scene.sceneRect()
        width = int(rect.width())
        height = int(rect.height())

        image = QImage(width, height, QImage.Format_ARGB32)

        if self.bg_color == "transparent":
            image.fill(QColor(0, 0, 0, 0))
        else:
            image.fill(QColor(self.bg_color))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        scene.render(painter, QRectF(image.rect()), rect)

        painter.end()

        image.save(filename, self.fmt)