from src.logic.shapes import Rectangle, Ellipse, Line, Group
from PySide6.QtCore import Qt


class ShapeFactory:
    @staticmethod
    def create_shape(shape_type, start_point, end_point, color):
        x1 = start_point.x();
        y1 = start_point.y()
        x2 = end_point.x();
        y2 = end_point.y()

        if shape_type == 'line':
            return Line(x1, y1, x2, y2, color)

        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)

        if shape_type == 'rect':
            return Rectangle(x, y, w, h, color)
        elif shape_type == 'ellipse':
            return Ellipse(x, y, w, h, color)
        else:
            raise ValueError(f"Неизвестный тип: {shape_type}")

    @staticmethod
    def from_dict(data: dict):
        shape_type = data.get("type")
        if shape_type == "group":
            return ShapeFactory._create_group(data)
        elif shape_type in ["rect", "ellipse", "line"]:
            return ShapeFactory._create_primitive(data)
        return None

    @staticmethod
    def _create_primitive(data: dict):
        shape_type = data["type"]
        coords = data["coords"]
        color = data["color"]
        width = data.get("width", 2)

        style_val = data.get("style", 1)
        style = Qt.PenStyle(style_val)

        obj = None
        if shape_type == "rect":
            obj = Rectangle(*coords, color)
        elif shape_type == "ellipse":
            obj = Ellipse(*coords, color)
        elif shape_type == "line":
            obj = Line(*coords, color)

        if obj and hasattr(obj, "set_stroke_width"):
            obj.set_stroke_width(width)

        if obj and hasattr(obj, "set_stroke_style"):
            obj.set_stroke_style(style)

        if "pos" in data:
            obj.setPos(data["pos"][0], data["pos"][1])

        return obj

    @staticmethod
    def _create_group(data: dict):
        group = Group()

        children_data = data.get("children", [])
        for child_dict in children_data:
            child_item = ShapeFactory.from_dict(child_dict)
            if child_item:
                group.addToGroup(child_item)

                if "pos" in child_dict:
                    child_item.setPos(child_dict["pos"][0], child_dict["pos"][1])

        if "pos" in data:
            group.setPos(data["pos"][0], data["pos"][1])

        return group