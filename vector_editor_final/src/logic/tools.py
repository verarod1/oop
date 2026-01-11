from PySide6.QtWidgets import QGraphicsItem, QGraphicsView
from PySide6.QtCore import Qt
from src.logic.factory import ShapeFactory
from src.logic.commands import AddShapeCommand, MoveCommand


class Tool:
    def __init__(self, canvas):
        self.canvas = canvas
        self.scene = canvas.scene

    def mouse_press(self, event): pass

    def mouse_move(self, event): pass

    def mouse_release(self, event): pass


class SelectionTool(Tool):
    def __init__(self, canvas, undo_stack):
        super().__init__(canvas)
        self.undo_stack = undo_stack
        self.item_positions = {}

    def mouse_press(self, event):
        self.item_positions.clear()

        for item in self.scene.selectedItems():
            self.item_positions[item] = item.pos()

        item = self.canvas.itemAt(event.pos())
        if item:
            self.canvas.setCursor(Qt.CursorShape.ClosedHandCursor)
            if item not in self.item_positions:
                self.item_positions[item] = item.pos()
        else:
            self.canvas.setCursor(Qt.CursorShape.ArrowCursor)

    def mouse_move(self, event):
        if not (event.buttons() & Qt.LeftButton):
            item = self.canvas.itemAt(event.pos())
            if item:
                self.canvas.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.canvas.setCursor(Qt.CursorShape.ArrowCursor)

    def mouse_release(self, event):
        item = self.canvas.itemAt(event.pos())
        if item:
            self.canvas.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.canvas.setCursor(Qt.CursorShape.ArrowCursor)

        moved_items = []
        for item, old_pos in self.item_positions.items():
            if item.scene() != self.scene: continue

            new_pos = item.pos()
            if new_pos != old_pos:
                moved_items.append((item, old_pos, new_pos))

        if moved_items:
            self.undo_stack.beginMacro("Move Items")
            for item, old_pos, new_pos in moved_items:
                self.undo_stack.push(MoveCommand(item, old_pos, new_pos))
            self.undo_stack.endMacro()

        self.item_positions.clear()


class CreationTool(Tool):
    def __init__(self, canvas, shape_type, undo_stack):
        super().__init__(canvas)
        self.shape_type = shape_type
        self.undo_stack = undo_stack
        self.current_item = None
        self.start_point = None

    def mouse_press(self, event):
        self.canvas.scene.clearSelection()
        self.start_point = self.canvas.mapToScene(event.pos())
        self.current_item = ShapeFactory.create_shape(
            self.shape_type,
            self.start_point,
            self.start_point,
            "black"
        )
        if self.current_item:
            self.current_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            self.current_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            self.scene.addItem(self.current_item)

    def mouse_move(self, event):
        if self.current_item and self.start_point:
            end_point = self.canvas.mapToScene(event.pos())
            self.current_item.set_geometry(self.start_point, end_point)

    def mouse_release(self, event):
        if self.current_item:
            self.current_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            self.current_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            self.scene.removeItem(self.current_item)

            cmd = AddShapeCommand(self.scene, self.current_item)
            self.undo_stack.push(cmd)

            self.current_item = None
            self.start_point = None

            if hasattr(self.canvas, "mouse_released"):
                self.canvas.mouse_released.emit()