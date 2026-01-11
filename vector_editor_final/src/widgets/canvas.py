from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter, QUndoStack
from PySide6.QtCore import Qt, Signal
from src.logic.tools import SelectionTool, CreationTool
from src.logic.shapes import Group
from src.logic.commands import DeleteCommand


class EditorCanvas(QGraphicsView):
    mouse_released = Signal()

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 800, 600)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(50)

        self.tools = {
            "select": SelectionTool(self, self.undo_stack),
            "rect": CreationTool(self, "rect", self.undo_stack),
            "line": CreationTool(self, "line", self.undo_stack),
            "ellipse": CreationTool(self, "ellipse", self.undo_stack)
        }

        self.current_tool = self.tools["select"]

    def set_tool(self, tool_name: str):
        if tool_name in self.tools:
            self.current_tool = self.tools[tool_name]
            if tool_name == "select":
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.scene.clearSelection()

    def mousePressEvent(self, event):
        if isinstance(self.current_tool, SelectionTool):
            self.current_tool.mouse_press(event)
            super().mousePressEvent(event)
        else:
            self.current_tool.mouse_press(event)

    def mouseMoveEvent(self, event):
        self.current_tool.mouse_move(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.current_tool.mouse_release(event)
        super().mouseReleaseEvent(event)
        self.mouse_released.emit()

    def group_selection(self):
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 1: return
        group = Group()
        self.scene.addItem(group)
        for item in selected_items:
            item.setSelected(False)
            group.addToGroup(item)
        group.setSelected(True)
        self.update()

    def ungroup_selection(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, Group):
                self.scene.destroyItemGroup(item)

    def delete_selected(self):
        selected = self.scene.selectedItems()
        if not selected:
            return

        self.undo_stack.beginMacro("Delete Selection")

        for item in selected:
            cmd = DeleteCommand(self.scene, item)
            self.undo_stack.push(cmd)

        self.undo_stack.endMacro()

    def select_all(self):
        for item in self.scene.items():
            item.setSelected(True)

    def clear_scene(self):
        self.scene.clear()
        self.undo_stack.clear()