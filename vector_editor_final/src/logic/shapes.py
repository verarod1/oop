from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup, QStyle
from PySide6.QtGui import QPen, QColor, QPainterPath
from PySide6.QtCore import Qt


class Shape(QGraphicsPathItem):
    def __init__(self, color="black", stroke_width=2, style=Qt.SolidLine):
        super().__init__()
        self.color = color
        self.stroke_width = stroke_width
        self.stroke_style = style
        self._setup_pen()
        self._setup_flags()

    def _setup_pen(self):
        pen = QPen(QColor(self.color))
        pen.setWidth(self.stroke_width)
        pen.setStyle(self.stroke_style)
        self.setPen(pen)

    def _setup_flags(self):
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def set_active_color(self, color: str):
        self.color = color
        self._setup_pen()

    def set_stroke_width(self, width: int):
        self.stroke_width = width
        self._setup_pen()

    def set_stroke_style(self, style):
        self.stroke_style = style
        self._setup_pen()

    def set_geometry(self, start_point, end_point):
        raise NotImplementedError

    @property
    def type_name(self) -> str:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError


class Group(QGraphicsItemGroup):
    def __init__(self):
        super().__init__()
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable, True)
        self.setHandlesChildEvents(True)

    @property
    def type_name(self) -> str:
        return "group"

    def set_geometry(self, start, end):
        pass

    def set_active_color(self, color: str):
        for child in self.childItems():
            if hasattr(child, "set_active_color"):
                child.set_active_color(color)

    def set_stroke_width(self, width: int):
        for child in self.childItems():
            if hasattr(child, "set_stroke_width"):
                child.set_stroke_width(width)

    def set_stroke_style(self, style):
        for child in self.childItems():
            if hasattr(child, "set_stroke_style"):
                child.set_stroke_style(style)

    def paint(self, painter, option, widget):
        if option.state & QStyle.State_Selected:
            painter.save()
            pen = QPen(Qt.black, 1, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
            painter.restore()

    def to_dict(self) -> dict:
        children_data = []
        for child in self.childItems():
            if hasattr(child, "to_dict"):
                children_data.append(child.to_dict())
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "children": children_data
        }


class Rectangle(Shape):
    def __init__(self, x, y, w, h, color="black"):
        super().__init__(color)
        self.x = x;
        self.y = y;
        self.w = w;
        self.h = h
        self._create_path()

    @property
    def type_name(self): return "rect"

    def _create_path(self):
        path = QPainterPath()
        path.addRect(self.x, self.y, self.w, self.h)
        self.setPath(path)

    def set_geometry(self, start_point, end_point):
        self.x = min(start_point.x(), end_point.x())
        self.y = min(start_point.y(), end_point.y())
        self.w = abs(end_point.x() - start_point.x())
        self.h = abs(end_point.y() - start_point.y())
        self._create_path()

    def to_dict(self):
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "coords": [self.x, self.y, self.w, self.h],
            "color": self.pen().color().name(),
            "width": self.pen().width(),
            "style": int(self.pen().style().value)
        }


class Ellipse(Shape):
    def __init__(self, x, y, w, h, color="black"):
        super().__init__(color)
        self.x = x;
        self.y = y;
        self.w = w;
        self.h = h
        self._create_path()

    @property
    def type_name(self): return "ellipse"

    def _create_path(self):
        path = QPainterPath()
        path.addEllipse(self.x, self.y, self.w, self.h)
        self.setPath(path)

    def set_geometry(self, start_point, end_point):
        self.x = min(start_point.x(), end_point.x())
        self.y = min(start_point.y(), end_point.y())
        self.w = abs(end_point.x() - start_point.x())
        self.h = abs(end_point.y() - start_point.y())
        self._create_path()

    def to_dict(self):
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "coords": [self.x, self.y, self.w, self.h],
            "color": self.pen().color().name(),
            "width": self.pen().width(),
            "style": int(self.pen().style().value)
        }


class Line(Shape):
    def __init__(self, x1, y1, x2, y2, color="black"):
        super().__init__(color)
        self.x1 = x1;
        self.y1 = y1;
        self.x2 = x2;
        self.y2 = y2
        self._create_path()

    @property
    def type_name(self): return "line"

    def _create_path(self):
        path = QPainterPath()
        path.moveTo(self.x1, self.y1)
        path.lineTo(self.x2, self.y2)
        self.setPath(path)

    def set_geometry(self, start_point, end_point):
        self.x1 = start_point.x()
        self.y1 = start_point.y()
        self.x2 = end_point.x()
        self.y2 = end_point.y()
        self._create_path()

    def to_dict(self):
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "coords": [self.x1, self.y1, self.x2, self.y2],
            "color": self.pen().color().name(),
            "width": self.pen().width(),
            "style": int(self.pen().style().value)
        }