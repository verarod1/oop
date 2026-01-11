import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFrame, QFileDialog, QMessageBox)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt
from src.widgets.canvas import EditorCanvas
from src.logic.file_manager import FileManager
from src.widgets.properties import PropertiesPanel
from src.logic.factory import ShapeFactory
from src.logic.strategies import JsonSaveStrategy, ImageSaveStrategy


class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Editor v0.1")
        self.resize(1000, 700)
        self._init_ui()

    def _init_ui(self):
        self.statusBar().showMessage("Готов к работе")

        container = QWidget()
        self.setCentralWidget(container)

        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tools_panel = QFrame()
        self.tools_panel.setFixedWidth(120)
        self.tools_panel.setStyleSheet("background-color: #26282e;")
        tools_layout = QVBoxLayout(self.tools_panel)

        self.btn_select = QPushButton("Select")
        self.btn_line = QPushButton("Line")
        self.btn_rect = QPushButton("Rect")
        self.btn_ellipse = QPushButton("Ellipse")

        for btn in [self.btn_select, self.btn_line, self.btn_rect, self.btn_ellipse]:
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton { color: white; border: 1px solid #555; padding: 5px; }
                QPushButton:checked { background-color: #3a86ff; border-color: #3a86ff; }
            """)
            tools_layout.addWidget(btn)

        self.btn_select.clicked.connect(lambda: self.on_change_tool("select"))
        self.btn_line.clicked.connect(lambda: self.on_change_tool("line"))
        self.btn_rect.clicked.connect(lambda: self.on_change_tool("rect"))
        self.btn_ellipse.clicked.connect(lambda: self.on_change_tool("ellipse"))
        tools_layout.addStretch()

        self.canvas = EditorCanvas()
        self.canvas.setStyleSheet("background-color: white;")

        self.props_panel = PropertiesPanel(self.canvas.scene, self.canvas.undo_stack)

        main_layout.addWidget(self.tools_panel)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.props_panel)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save As...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")

        stack = self.canvas.undo_stack

        undo_action = stack.createUndoAction(self, "&Undo")
        undo_action.setShortcut(QKeySequence.Undo)
        redo_action = stack.createRedoAction(self, "&Redo")
        redo_action.setShortcut(QKeySequence.Redo)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.canvas.select_all)
        edit_menu.addAction(select_all_action)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.canvas.delete_selected)
        edit_menu.addAction(delete_action)
        self.addAction(delete_action)

        edit_menu.addSeparator()

        group_action = QAction("Group", self)
        group_action.setShortcut(QKeySequence("Ctrl+G"))
        group_action.triggered.connect(self.canvas.group_selection)
        edit_menu.addAction(group_action)

        ungroup_action = QAction("Ungroup", self)
        ungroup_action.setShortcut(QKeySequence("Ctrl+U"))
        ungroup_action.triggered.connect(self.canvas.ungroup_selection)
        edit_menu.addAction(ungroup_action)

        self.canvas.mouse_released.connect(self.props_panel.on_selection_changed)

        self.btn_line.click()

    def on_change_tool(self, tool_name):
        self.btn_select.setChecked(tool_name == "select")
        self.btn_line.setChecked(tool_name == "line")
        self.btn_rect.setChecked(tool_name == "rect")
        self.btn_ellipse.setChecked(tool_name == "ellipse")
        self.canvas.set_tool(tool_name)

    def new_file(self):
        reply = QMessageBox.question(self, 'Новый файл',
                                     "Все несохраненные изменения будут потеряны.\nСоздать новый файл?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.canvas.clear_scene()
            self.statusBar().showMessage("Создан новый файл")

    def save_file(self):
        filters = "Vector Project (*.json *.vec);;PNG Image (*.png);;JPEG Image (*.jpg)"
        file_path, selected_filter = QFileDialog.getSaveFileName(self, "Save File", "", filters)

        if not file_path:
            return

        strategy = None
        if file_path.lower().endswith(".png"):
            strategy = ImageSaveStrategy("PNG", bg_color="transparent")
        elif file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg"):
            strategy = ImageSaveStrategy("JPG", bg_color="white")
        else:
            strategy = JsonSaveStrategy()

        try:
            strategy.save(file_path, self.canvas.scene)
            self.statusBar().showMessage(f"Saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Vector Project (*.vec *.json)")
        if not file_path:
            return

        try:
            project_data = FileManager.load_project(file_path)

            self.canvas.scene.clear()
            if hasattr(self.canvas, "undo_stack"):
                self.canvas.undo_stack.clear()

            shapes_data = project_data.get("shapes", [])
            loaded_count = 0
            for shape_dict in shapes_data:
                try:
                    new_shape = ShapeFactory.from_dict(shape_dict)
                    if new_shape:
                        self.canvas.scene.addItem(new_shape)
                        loaded_count += 1
                except Exception as e:
                    print(f"Error loading shape: {e}")

            self.statusBar().showMessage(f"Loaded {loaded_count} objects")

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load file:\n{str(e)}")