from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import Qt

class AddShapeCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        name = "Shape"
        if hasattr(item, "type_name"):
            name = item.type_name.capitalize()
        self.setText(f"Add {name}")

    def redo(self):
        if self.item.scene() != self.scene:
            self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class MoveCommand(QUndoCommand):
    def __init__(self, item, old_pos, new_pos):
        super().__init__()
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.setText(f"Move {item.type_name}")

    def undo(self):
        self.item.setPos(self.old_pos)

    def redo(self):
        self.item.setPos(self.new_pos)

class DeleteCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        name = "Item"
        if hasattr(item, "type_name"):
            name = item.type_name
        self.setText(f"Delete {name}")

    def redo(self):
        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)

class ChangeColorCommand(QUndoCommand):
    def __init__(self, item, new_color):
        super().__init__()
        self.item = item
        self.new_color = new_color
        if hasattr(item, "pen") and item.pen():
            self.old_color = item.pen().color().name()
        else:
            self.old_color = "#000000"
        self.setText(f"Change Color")

    def redo(self):
        if hasattr(self.item, "set_active_color"):
            self.item.set_active_color(self.new_color)

    def undo(self):
        if hasattr(self.item, "set_active_color"):
            self.item.set_active_color(self.old_color)

class ChangeWidthCommand(QUndoCommand):
    def __init__(self, item, new_width):
        super().__init__()
        self.item = item
        self.new_width = new_width
        if hasattr(item, "pen") and item.pen():
            self.old_width = item.pen().width()
        else:
            self.old_width = 1
        self.setText(f"Change Width")

    def redo(self):
        if hasattr(self.item, "set_stroke_width"):
            self.item.set_stroke_width(self.new_width)

    def undo(self):
        if hasattr(self.item, "set_stroke_width"):
            self.item.set_stroke_width(self.old_width)

class ChangeStyleCommand(QUndoCommand):
    def __init__(self, item, new_style):
        super().__init__()
        self.item = item
        self.new_style = new_style
        if hasattr(item, "pen") and item.pen():
            self.old_style = item.pen().style()
        else:
            self.old_style = Qt.SolidLine
        self.setText(f"Change Style")

    def redo(self):
        if hasattr(self.item, "set_stroke_style"):
            self.item.set_stroke_style(self.new_style)

    def undo(self):
        if hasattr(self.item, "set_stroke_style"):
            self.item.set_stroke_style(self.old_style)