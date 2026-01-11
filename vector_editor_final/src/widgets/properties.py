from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QSpinBox, QDoubleSpinBox, QPushButton, QColorDialog,
                               QFrame, QComboBox)
from PySide6.QtCore import Qt, QPointF
from src.logic.commands import ChangeColorCommand, ChangeWidthCommand, ChangeStyleCommand
from src.logic.shapes import Group


class PropertiesPanel(QWidget):
    def __init__(self, scene, undo_stack):
        super().__init__()
        self.scene = scene
        self.undo_stack = undo_stack
        self._init_ui()

        self.scene.selectionChanged.connect(self.on_selection_changed)

    def _init_ui(self):
        self.setFixedWidth(200)

        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; border-left: 1px solid #ccc; color: black; }
            QWidget:disabled { color: #888888; }
            QLabel { color: black; border: none; font-size: 13px; }
            QLabel:disabled { color: #888888; }
            QComboBox, QSpinBox, QDoubleSpinBox { 
                background-color: white; 
                border: 1px solid #999; 
                padding: 3px; 
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Тип объекта:"))
        self.lbl_type = QLabel("Ничего не выбрано")
        self.lbl_type.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.lbl_type)

        layout.addWidget(QLabel("Глобальные координаты:"))
        geo_layout = QHBoxLayout()
        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.setPrefix("X: ")
        self.spin_x.setDecimals(1)
        self.spin_x.valueChanged.connect(self.on_geo_changed)
        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.setPrefix("Y: ")
        self.spin_y.setDecimals(1)
        self.spin_y.valueChanged.connect(self.on_geo_changed)
        geo_layout.addWidget(self.spin_x)
        geo_layout.addWidget(self.spin_y)
        layout.addLayout(geo_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #ccc; margin: 10px 0;")
        layout.addWidget(line)

        layout.addWidget(QLabel("Толщина:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(1, 50)
        self.spin_width.valueChanged.connect(self.on_width_changed)
        layout.addWidget(self.spin_width)

        layout.addWidget(QLabel("Стиль:"))
        self.combo_style = QComboBox()
        self.combo_style.addItem("Solid (Сплошная)", Qt.SolidLine)
        self.combo_style.addItem("Dash (Штрих)", Qt.DashLine)
        self.combo_style.addItem("Dot (Точки)", Qt.DotLine)
        self.combo_style.addItem("DashDot (Штрих-пунктир)", Qt.DashDotLine)
        self.combo_style.currentIndexChanged.connect(self.on_style_changed)
        layout.addWidget(self.combo_style)

        layout.addWidget(QLabel("Цвет:"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedHeight(30)
        self.btn_color.setStyleSheet("border: 1px solid gray; background-color: transparent;")
        self.btn_color.clicked.connect(self.on_color_clicked)
        layout.addWidget(self.btn_color)

        layout.addStretch()
        self.setEnabled(False)

    def _get_visual_top_left(self, item):
        if hasattr(item, "path"):
            return item.path().boundingRect().topLeft()
        else:
            return item.boundingRect().topLeft()

    def _get_common_color(self, item):
        if isinstance(item, Group):
            children = item.childItems()
            if not children:
                return None

            first_color = self._get_common_color(children[0])
            if first_color is None:
                return None

            for child in children[1:]:
                if self._get_common_color(child) != first_color:
                    return None

            return first_color

        if hasattr(item, "pen") and item.pen() is not None:
            return item.pen().color().name()

        return None

    def on_selection_changed(self):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.setEnabled(False)
            self.lbl_type.setText("Ничего не выбрано")
            self._reset_values()
            return

        self.setEnabled(True)
        item = selected_items[0]

        t_name = item.type_name.upper() if hasattr(item, "type_name") else type(item).__name__
        if len(selected_items) > 1: t_name += f" (+{len(selected_items) - 1})"
        self.lbl_type.setText(t_name)

        self.spin_x.blockSignals(True)
        self.spin_y.blockSignals(True)
        local_anchor = self._get_visual_top_left(item)
        global_anchor = item.mapToScene(local_anchor)
        self.spin_x.setValue(global_anchor.x())
        self.spin_y.setValue(global_anchor.y())
        self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(False)

        current_width = 1
        current_style = Qt.SolidLine

        detected_color = self._get_common_color(item)
        current_color = detected_color if detected_color else "#000000"

        if hasattr(item, "pen") and item.pen() is not None:
            pen = item.pen()
            current_width = pen.width()
            current_style = pen.style()
        elif isinstance(item, Group):
            children = item.childItems()
            if children and hasattr(children[0], "pen"):
                current_width = children[0].pen().width()
                current_style = children[0].pen().style()

        self.spin_width.blockSignals(True)
        self.spin_width.setValue(current_width)
        self.spin_width.blockSignals(False)

        self.combo_style.blockSignals(True)
        idx = self.combo_style.findData(current_style)
        if idx != -1: self.combo_style.setCurrentIndex(idx)
        self.combo_style.blockSignals(False)

        self.btn_color.setStyleSheet(f"background-color: {current_color}; border: 1px solid gray;")

    def _reset_values(self):
        self.spin_x.blockSignals(True)
        self.spin_y.blockSignals(True)
        self.spin_x.setValue(0)
        self.spin_y.setValue(0)
        self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(False)
        self.spin_width.blockSignals(True)
        self.spin_width.setValue(1)
        self.spin_width.blockSignals(False)
        self.combo_style.blockSignals(True)
        self.combo_style.setCurrentIndex(0)
        self.combo_style.blockSignals(False)
        self.btn_color.setStyleSheet("border: 1px solid gray; background-color: transparent;")

    def on_geo_changed(self):
        selected_items = self.scene.selectedItems()
        target_pos = QPointF(self.spin_x.value(), self.spin_y.value())
        for item in selected_items:
            local_anchor = self._get_visual_top_left(item)
            current_global_pos = item.mapToScene(local_anchor)
            delta = target_pos - current_global_pos
            item.setPos(item.pos() + delta)
        self.scene.update()

    def on_width_changed(self, value):
        selected = self.scene.selectedItems()
        if not selected: return

        self.undo_stack.beginMacro("Change Width")
        for item in selected:
            cmd = ChangeWidthCommand(item, value)
            self.undo_stack.push(cmd)
        self.undo_stack.endMacro()

        self.scene.update()

    def on_style_changed(self, index):
        selected = self.scene.selectedItems()
        if not selected: return

        style = self.combo_style.currentData()

        self.undo_stack.beginMacro("Change Style")
        for item in selected:
            cmd = ChangeStyleCommand(item, style)
            self.undo_stack.push(cmd)
        self.undo_stack.endMacro()

        self.scene.update()

    def on_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_c = color.name()
            self.btn_color.setStyleSheet(f"background-color: {hex_c}; border: 1px solid gray;")

            selected = self.scene.selectedItems()
            if not selected: return

            self.undo_stack.beginMacro("Change Color")
            for item in selected:
                cmd = ChangeColorCommand(item, hex_c)
                self.undo_stack.push(cmd)
            self.undo_stack.endMacro()

            self.scene.update()