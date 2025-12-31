import sys
import math
from itertools import permutations
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QDialog, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPalette, QCursor


class GraphWidget(QWidget):
    edge_clicked = Signal(int, int)
    add_edge_requested = Signal(int, int)

    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix
        self.n = len(matrix)
        self.positions = []
        self.selected_vertex = -1
        self.dragging = False
        self.edit_mode = "view"
        self.temp_edge_start = -1
        self.node_radius = 20
        self.hovered_edge = (-1, -1)
        self.setMinimumSize(500, 500)
        self.setMouseTracking(True)
        self.update_positions()

    def update_positions(self):
        self.positions.clear()
        if self.n == 0:
            return
        center_x, center_y = self.width() // 2, self.height() // 2
        radius = min(center_x, center_y) - 60
        for i in range(self.n):
            angle = 2 * math.pi * i / self.n - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.positions.append(QPoint(int(x), int(y)))

    def resizeEvent(self, event):
        self.update_positions()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for i in range(self.n):
            for j in range(i + 1, self.n):
                weight = self.matrix[i][j]
                if weight is not None and weight != 0:
                    if self.edit_mode == "delete_edge" and self.hovered_edge == (i, j):
                        pen = QPen(QColor(255, 0, 0), 3)
                    elif self.edit_mode == "delete_edge":
                        pen = QPen(QColor(200, 0, 0), 2)
                    else:
                        pen = QPen(QColor(0, 0, 0), 2)
                    painter.setPen(pen)
                    painter.drawLine(self.positions[i], self.positions[j])
                    if weight > 0:
                        mid_x = (self.positions[i].x() + self.positions[j].x()) // 2
                        mid_y = (self.positions[i].y() + self.positions[j].y()) // 2
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QBrush(Qt.white))
                        painter.drawEllipse(mid_x - 15, mid_y - 10, 30, 20)
                        painter.setPen(QPen(Qt.red))
                        painter.setFont(QFont("Arial", 9, QFont.Bold))
                        painter.drawText(mid_x - 15, mid_y - 10, 30, 20, Qt.AlignCenter, str(weight))
        if self.edit_mode == "add_edge" and self.temp_edge_start >= 0:
            painter.setPen(QPen(QColor(0, 200, 0), 2, Qt.DashLine))
            mouse_pos = self.mapFromGlobal(QCursor.pos())
            painter.drawLine(self.positions[self.temp_edge_start], mouse_pos)
        for i, pos in enumerate(self.positions):
            if i == self.selected_vertex:
                brush = QBrush(QColor(255, 255, 0))
            elif self.edit_mode == "add_edge" and self.temp_edge_start == i:
                brush = QBrush(QColor(0, 255, 0))
            elif self.edit_mode == "add_edge":
                brush = QBrush(QColor(200, 255, 200))
            else:
                brush = QBrush(QColor(100, 150, 255))
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(brush)
            painter.drawEllipse(pos, self.node_radius, self.node_radius)
            painter.setPen(QPen(Qt.black))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(pos.x() - 10, pos.y() - 10, 20, 20, Qt.AlignCenter, str(i + 1))

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        if self.edit_mode == "view":
            for i, vertex_pos in enumerate(self.positions):
                if self.distance(pos, vertex_pos) <= self.node_radius:
                    self.selected_vertex = i
                    self.dragging = True
                    self.update()
                    break
        elif self.edit_mode == "delete_edge":
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    if self.matrix[i][j] not in (None, 0):
                        if self.is_point_on_line(pos, self.positions[i], self.positions[j]):
                            self.edge_clicked.emit(i, j)
                            return
        elif self.edit_mode == "add_edge":
            for i, vertex_pos in enumerate(self.positions):
                if self.distance(pos, vertex_pos) <= self.node_radius:
                    if self.temp_edge_start == -1:
                        self.temp_edge_start = i
                        self.update()
                    else:
                        if i != self.temp_edge_start:
                            if self.matrix[self.temp_edge_start][i] in (None, 0):
                                self.add_edge_requested.emit(self.temp_edge_start, i)
                        self.temp_edge_start = -1
                        self.update()
                    break

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self.dragging and self.selected_vertex >= 0:
            self.positions[self.selected_vertex] = pos
            self.update()
        elif self.edit_mode == "delete_edge":
            old_hover = self.hovered_edge
            self.hovered_edge = (-1, -1)
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    if self.matrix[i][j] not in (None, 0):
                        if self.is_point_on_line(pos, self.positions[i], self.positions[j]):
                            self.hovered_edge = (i, j)
                            break
                if self.hovered_edge != (-1, -1):
                    break
            if old_hover != self.hovered_edge:
                self.update()
        else:
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        if self.selected_vertex >= 0:
            self.selected_vertex = -1
            self.update()

    def set_edit_mode(self, mode):
        self.edit_mode = mode
        self.temp_edge_start = -1
        self.hovered_edge = (-1, -1)
        self.update()

    def update_matrix(self, new_matrix):
        self.matrix = new_matrix
        self.n = len(new_matrix)
        self.update_positions()
        self.update()

    def distance(self, p1, p2):
        return math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)

    def is_point_on_line(self, point, p1, p2, tolerance=8):
        line_length = self.distance(p1, p2)
        if line_length == 0:
            return False
        t = max(0, min(1, ((point.x() - p1.x()) * (p2.x() - p1.x()) +
                           (point.y() - p1.y()) * (p2.y() - p1.y())) / (line_length ** 2)))
        closest_x = p1.x() + t * (p2.x() - p1.x())
        closest_y = p1.y() + t * (p2.y() - p1.y())
        return self.distance(point, QPoint(int(closest_x), int(closest_y))) <= tolerance


class MatrixTable(QTableWidget):
    matrix_changed = Signal()

    def __init__(self, size):
        super().__init__(size, size + 1)
        self.size = size
        self.setup_table()
        self.cellChanged.connect(self.on_cell_changed)

    def setup_table(self):
        headers = ["Вершина"] + [f"{i + 1}" for i in range(self.size)]
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels([f"{i + 1}" for i in range(self.size)])
        for i in range(self.size):
            for j in range(self.size + 1):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)
                if j == 0:
                    item.setText(f"{i + 1}")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                elif i == j - 1:
                    item.setText("-")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                else:
                    item.setText("")
                self.setItem(i, j, item)
        self.resizeColumnsToContents()

    def on_cell_changed(self, row, column):
        if column > 0 and row != column - 1:
            item = self.item(row, column)
            if item:
                text = item.text().strip()
                if text == "" or text == "-":
                    item.setText("")
                elif not text.isdigit():
                    item.setText("")
                self.matrix_changed.emit()

    def get_matrix(self):
        matrix = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                if i == j:
                    row.append(None)
                else:
                    item = self.item(i, j + 1)
                    if item:
                        text = item.text().strip()
                        if text == "" or text == "-":
                            row.append(None)
                        elif text.isdigit():
                            row.append(int(text))
                        else:
                            row.append(None)
                    else:
                        row.append(None)
            matrix.append(row)
        return matrix

    def set_matrix(self, matrix):
        for i in range(self.size):
            for j in range(self.size):
                if i != j:
                    item = self.item(i, j + 1)
                    if item:
                        value = matrix[i][j]
                        item.setText("" if value is None or value == 0 else str(value))
        self.resizeColumnsToContents()


class GraphRoad:
    def __init__(self, rows, adjacency_list):
        self.rows = rows
        self.adjacency_list_A = adjacency_list
        self.adjacency_list_1 = ""

    def matrix_to_adjacency_list(self):
        n = len(self.rows)
        parts = []
        for i in range(n):
            neighbors = []
            for j in range(n):
                if self.rows[i][j] is not None and self.rows[i][j] > 0:
                    neighbors.append(str(j + 1))
            parts.append(str(i + 1) + ''.join(sorted(neighbors)))
        self.adjacency_list_1 = ' '.join(parts)

    def solve(self):
        self.matrix_to_adjacency_list()
        input_parts = [p for p in self.adjacency_list_A.upper().split() if p]
        input_list = ' '.join(input_parts)

        def normalize_list(lst):
            parts = lst.split()
            normalized = [p[0] + ''.join(sorted(list(p[1:]))) for p in parts if p]
            return ' '.join(sorted(normalized))

        n = len(self.rows)
        letters = [chr(ord('А') + i) for i in range(n)]
        for perm in permutations(letters):
            mapping = {str(d): perm[d - 1] for d in range(1, n + 1)}
            transformed = self.adjacency_list_1
            for digit, letter in mapping.items():
                transformed = transformed.replace(digit, letter)
            if normalize_list(transformed) == normalize_list(input_list):
                return ''.join([mapping[str(i + 1)] for i in range(n)])
        return "Совпадений не найдено"


class AddEdgeDialog(QDialog):
    def __init__(self, v1, v2, parent=None):
        super().__init__(parent)
        self.v1 = v1
        self.v2 = v2
        self.weight = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Добавить ребро")
        self.setModal(True)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Введите вес ребра между вершинами {self.v1 + 1} и {self.v2 + 1}:"))
        self.weight_input = QSpinBox()
        self.weight_input.setRange(1, 100)
        self.weight_input.setValue(1)
        layout.addWidget(self.weight_input)
        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def accept(self):
        self.weight = self.weight_input.value()
        super().accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графы")
        self.setGeometry(100, 100, 1200, 700)
        self.size = 7
        self.setup_ui()
        self.load_example()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.addWidget(QLabel("Количество вершин:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(3, 15)
        self.size_spin.setValue(7)
        self.size_spin.valueChanged.connect(self.change_size)
        size_layout.addWidget(self.size_spin)
        left_layout.addWidget(size_widget)
        self.matrix_container = QWidget()
        matrix_layout = QVBoxLayout(self.matrix_container)
        self.matrix_table = MatrixTable(self.size)
        self.matrix_table.matrix_changed.connect(self.on_matrix_changed)
        self.matrix_table.setFixedHeight(400)
        matrix_layout.addWidget(self.matrix_table)
        mode_layout = QHBoxLayout()
        self.view_btn = QPushButton("Просмотр")
        self.view_btn.setCheckable(True)
        self.view_btn.setChecked(True)
        self.view_btn.clicked.connect(lambda: self.set_mode("view"))
        self.add_edge_btn = QPushButton("Добавить ребро")
        self.add_edge_btn.setCheckable(True)
        self.add_edge_btn.clicked.connect(lambda: self.set_mode("add_edge"))
        self.delete_edge_btn = QPushButton("Удалить ребро")
        self.delete_edge_btn.setCheckable(True)
        self.delete_edge_btn.clicked.connect(lambda: self.set_mode("delete_edge"))
        mode_layout.addWidget(self.view_btn)
        mode_layout.addWidget(self.add_edge_btn)
        mode_layout.addWidget(self.delete_edge_btn)
        matrix_layout.addLayout(mode_layout)
        left_layout.addWidget(self.matrix_container)
        calc_widget = QWidget()
        calc_layout = QVBoxLayout(calc_widget)
        calc_layout.addWidget(QLabel("Список смежности:"))
        self.adjacency_input = QLineEdit()
        self.adjacency_input.setPlaceholderText("Пример: АБВГ БАД ...")
        calc_layout.addWidget(self.adjacency_input)
        examples_combo = QComboBox()
        examples_combo.addItem("Выберите пример...")
        examples_combo.addItem("Простой пример (6 вершин)")
        examples_combo.currentTextChanged.connect(self.load_example_from_combo)
        calc_layout.addWidget(examples_combo)
        self.calc_btn = QPushButton("Решить")
        self.calc_btn.clicked.connect(self.calculate)
        calc_layout.addWidget(self.calc_btn)
        self.result_label = QLabel("Ответ: ")
        self.result_label.setAlignment(Qt.AlignCenter)
        calc_layout.addWidget(self.result_label)
        left_layout.addWidget(calc_widget)
        left_layout.addStretch()
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        graph_widget = QWidget()
        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_widget = GraphWidget(self.matrix_table.get_matrix())
        self.graph_widget.edge_clicked.connect(self.delete_edge)
        self.graph_widget.add_edge_requested.connect(self.add_edge_dialog)
        self.graph_layout.addWidget(self.graph_widget)
        graph_scroll = QScrollArea()
        graph_scroll.setWidgetResizable(True)
        graph_scroll.setWidget(self.graph_container)
        right_layout.addWidget(graph_scroll)
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def load_example(self):
        matrix = [
            [None, None, 15, None, None, None, 20],
            [None, None, None, None, None, 22, 18],
            [15, None, None, None, None, None, 10],
            [None, None, None, None, 9, 8, None],
            [None, None, None, 9, None, None, 12],
            [None, 22, None, 8, None, None, 14],
            [20, 18, 10, None, 12, 14, None]
        ]
        self.matrix_table.set_matrix(matrix)
        self.adjacency_input.setText("АБВГ БАД ВАГ ГАВДЕК ДБГ ЕГК КЕГ")
        self.on_matrix_changed()

    def load_example_from_combo(self, text):
        if text == "Простой пример (6 вершин)":
            self.size_spin.setValue(6)
            matrix = [
                [None, None, 12, 6, 15, 13],
                [None, None, None, None, None, 11],
                [12, None, None, None, 9, None],
                [6, None, None, None, 7, 5],
                [15, None, 9, 7, None, None],
                [13, 11, None, 5, None, None]
            ]
            self.matrix_table.set_matrix(matrix)
            self.adjacency_input.setText("АБВ БАВГ ВАБГД ГБВД ДВГЕ ЕД")
            self.on_matrix_changed()

    def change_size(self):
        new_size = self.size_spin.value()
        self.size = new_size
        old_matrix = self.matrix_table.get_matrix()
        self.matrix_table.matrix_changed.disconnect()
        old_table = self.matrix_container.layout().takeAt(0).widget()
        if old_table:
            old_table.deleteLater()
        self.matrix_table = MatrixTable(new_size)
        self.matrix_table.matrix_changed.connect(self.on_matrix_changed)
        self.matrix_table.setFixedHeight(400)
        self.matrix_container.layout().insertWidget(0, self.matrix_table)
        new_matrix = []
        for i in range(new_size):
            row = []
            for j in range(new_size):
                if i < len(old_matrix) and j < len(old_matrix) and j < len(old_matrix[i]):
                    row.append(old_matrix[i][j])
                else:
                    row.append(None)
            new_matrix.append(row)
        self.matrix_table.set_matrix(new_matrix)
        self.on_matrix_changed()

    def on_matrix_changed(self):
        self.graph_widget.update_matrix(self.matrix_table.get_matrix())

    def set_mode(self, mode):
        self.view_btn.setChecked(mode == "view")
        self.add_edge_btn.setChecked(mode == "add_edge")
        self.delete_edge_btn.setChecked(mode == "delete_edge")
        self.graph_widget.set_edit_mode(mode)

    def add_edge_dialog(self, v1, v2):
        dialog = AddEdgeDialog(v1, v2, self)
        if dialog.exec() == QDialog.Accepted and dialog.weight is not None:
            self.matrix_table.setItem(v1, v2 + 1, QTableWidgetItem(str(dialog.weight)))
            self.matrix_table.setItem(v2, v1 + 1, QTableWidgetItem(str(dialog.weight)))
            self.on_matrix_changed()

    def delete_edge(self, v1, v2):
        self.matrix_table.setItem(v1, v2 + 1, QTableWidgetItem(""))
        self.matrix_table.setItem(v2, v1 + 1, QTableWidgetItem(""))
        self.on_matrix_changed()

    def calculate(self):
        matrix = self.matrix_table.get_matrix()
        adjacency_str = self.adjacency_input.text().strip()
        result = GraphRoad(matrix, adjacency_str).solve()
        self.result_label.setText(f"Ответ: {result}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(60, 60, 60))
    palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()