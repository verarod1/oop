import sys
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MathSolver:
    def __init__(self):
        self.context = {
            'isIn': self.isIn,
            'n': lambda x: not x
        }

    @staticmethod
    def isIn(x, interval):
        return interval[0] <= x <= interval[1]

    def prepare_expression(self, expression: str) -> str:
        expr = re.sub(r'([a-zA-Z0-9_]+)\s*∈\s*([a-zA-Z0-9_]+)', r'isIn(\1, \2)', expression)
        replacements = {
            '¬': ' n',
            '∧': ' and ',
            '∨': ' or ',
            '≡': ' == ',
            '→': ' <= ',
            '->': ' <= ',
            '==': ' == ',
            '!=': ' != '
        }
        for k, v in replacements.items():
            expr = expr.replace(k, v)
        return expr

    def solve_task(self, P, Q, expression) -> str:
        py_expr = self.prepare_expression(expression)
        all_coords = [P[0], P[1], Q[0], Q[1]]
        min_val = int(min(all_coords))
        max_val = int(max(all_coords))

        search_start = min_val - 5
        search_end = max_val + 5
        valid_lengths = []

        for start in range(search_start, search_end + 1):
            for end in range(start, search_end + 1):
                current_A = (start, end)
                is_valid_A = True
                check_range = range(search_start * 2, (search_end + 1) * 2)

                for k in check_range:
                    x = k / 2.0
                    local_vars = {
                        'x': x,
                        'P': P,
                        'Q': Q,
                        'A': current_A,
                    }
                    full_context = {**self.context, **local_vars}

                    if not eval(py_expr, {}, full_context):
                        is_valid_A = False
                        break

                if is_valid_A:
                    valid_lengths.append(end - start)

        if not valid_lengths:
            return "Решений не найдено."

        return (f"Максимальная длина: {max(valid_lengths)}")


class IntervalInput(QWidget):
    def __init__(self, label="Отрезок"):
        super().__init__()
        self.label = label
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label_widget = QLabel(f"{self.label}:")
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Начало")
        self.start_input.setFixedWidth(80)
        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("Конец")
        self.end_input.setFixedWidth(80)
        layout.addWidget(self.label_widget)
        layout.addWidget(QLabel("["))
        layout.addWidget(self.start_input)
        layout.addWidget(QLabel(","))
        layout.addWidget(self.end_input)
        layout.addWidget(QLabel("]"))
        layout.addStretch()
        self.setLayout(layout)

    def get_interval(self):
        start = float(self.start_input.text().strip())
        end = float(self.end_input.text().strip())
        return start, end

    def set_interval(self, start, end):
        self.start_input.setText(str(start))
        self.end_input.setText(str(end))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.solver = MathSolver()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Решатель задачи на отрезки')
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        title = QLabel('Решение задачи №15 на отрезки')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        input_group = QGroupBox('Входные данные')
        input_layout = QFormLayout()
        input_layout.setSpacing(10)

        self.P_input = IntervalInput("Отрезок P")
        input_layout.addRow('Отрезок P:', self.P_input)
        self.P_input.set_interval(25, 50)

        self.Q_input = IntervalInput("Отрезок Q")
        input_layout.addRow('Отрезок Q:', self.Q_input)
        self.Q_input.set_interval(32, 47)

        self.expression_input = QLineEdit()
        self.expression_input.setPlaceholderText("Введите формулу")
        self.expression_input.setText("(¬ (x ∈ A) → (x ∈ P)) → ((x ∈ A) → (x ∈ Q))")
        input_layout.addRow('Выражение:', self.expression_input)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        self.solve_button = QPushButton('Найти решение')
        self.solve_button.clicked.connect(self.solve_problem)
        self.solve_button.setFixedHeight(40)
        solve_button_font = QFont()
        solve_button_font.setPointSize(12)
        solve_button_font.setBold(True)
        self.solve_button.setFont(solve_button_font)
        main_layout.addWidget(self.solve_button)

        output_group = QGroupBox('Результат')
        output_layout = QVBoxLayout()

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMinimumHeight(300)
        output_layout.addWidget(self.result_display)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        central_widget.setLayout(main_layout)

    def solve_problem(self):
        P = self.P_input.get_interval()
        Q = self.Q_input.get_interval()
        expression = self.expression_input.text().strip()
        result = self.solver.solve_task(P, Q, expression)
        self.result_display.setPlainText(result)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()