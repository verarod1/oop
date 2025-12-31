import tkinter as tk
from tkinter import ttk, messagebox
from functools import lru_cache
from math import floor


@lru_cache(None)
def f(a, b, operations, win_value,win_condition):
    total = a + (b if b is not None else 0)
    win_value1 = int(win_value)
    if (win_condition == ">=" and total >= win_value) or \
            (win_condition == ">" and total > win_value) or \
            (win_condition == "<=" and total <= win_value) or \
            (win_condition == "<" and total < win_value) or \
            (win_condition == "=" and total == win_value) or \
            (win_condition == "!=" and total != win_value):
        return 0
    t = []
    for i in operations:
        if i[0]!='/':
            h1 = str(a) + i
            h1 = eval(h1)
        else:
            h1=a/int(i[1:])
            h1=floor(h1)
        if b!=0 and b is not None:
            h2 = str(b) + i
            h2 = eval(h2)
            t.append(f(a, h2, operations, win_value1,win_condition))
        t.append(f(h1, b, operations, win_value1,win_condition))
    n = [i for i in t if i <= 0]
    if n:
        return -max(n) + 1
    return -max(t)


class EgeSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Решатель заданий 19-21 ЕГЭ по информатике")
        self.root.geometry("800x600")
        self.heap_var = tk.StringVar(value="1")
        self.bad_move_var = tk.BooleanVar(value=False)
        self.win_condition_var = tk.StringVar(value=">=")
        self.win_value_var = tk.StringVar(value="132")
        self.heap2 = tk.StringVar(value="5")
        self.operations = []
        self.calculate_19_func = None
        self.calculate_20_func = None
        self.calculate_21_func = None
        self.heap2_frame = None
        self.create_widgets()
        self.heap_var.trace('w', self.on_heap_change)

    def on_heap_change(self, *args):
        if self.heap_var.get() == "2":
            self.show_heap2_frame()
        else:
            self.hide_heap2_frame()

    def show_heap2_frame(self):
        if self.heap2_frame is None:
            self.heap2_frame = ttk.LabelFrame(self.main_frame, text="Начальное значение второй кучи", padding="10")
            ttk.Label(self.heap2_frame, text="Начальное значение второй кучи:").pack(side=tk.LEFT, padx=5)
            ttk.Entry(self.heap2_frame, textvariable=self.heap2, width=10).pack(side=tk.LEFT, padx=5)
        self.heap2_frame.pack(fill=tk.X, pady=5, after=self.heap_frame)

    def hide_heap2_frame(self):
        if self.heap2_frame:
            self.heap2_frame.pack_forget()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(self.main_frame, text="Универсальный решатель заданий 19-21 ЕГЭ",
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        heap_frame = ttk.LabelFrame(self.main_frame, text="Выбор кучи", padding="10")
        heap_frame.pack(fill=tk.X, pady=5)
        self.heap_frame = heap_frame

        ttk.Radiobutton(heap_frame, text="Одна куча", variable=self.heap_var,
                        value="1").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(heap_frame, text="Две кучи", variable=self.heap_var,
                        value="2").pack(side=tk.LEFT, padx=10)

        win_frame = ttk.LabelFrame(self.main_frame, text="Условие победы", padding="10")
        win_frame.pack(fill=tk.X, pady=5)
        self.win_frame = win_frame

        win_subframe = ttk.Frame(win_frame)
        win_subframe.pack(fill=tk.X)
        ttk.Label(win_subframe, text="Победа, когда камней").pack(side=tk.LEFT)
        ttk.Combobox(win_subframe, textvariable=self.win_condition_var,
                     values=[">", ">=", "<", "<=", "=", "!="], width=5).pack(side=tk.LEFT, padx=5)
        ttk.Entry(win_subframe, textvariable=self.win_value_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(win_subframe, text="(S - для одной кучи, S1+S2 - для двух куч)").pack(side=tk.LEFT, padx=5)

        bad_move_frame = ttk.LabelFrame(self.main_frame, text="Неудачный ход", padding="10")
        bad_move_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(bad_move_frame, text="Был неудачный ход в игре",
                        variable=self.bad_move_var).pack(anchor=tk.W)

        operations_frame = ttk.LabelFrame(self.main_frame, text="Операции (для Васи и Пети)", padding="10")
        operations_frame.pack(fill=tk.X, pady=5)
        self.create_operations_widgets(operations_frame)

        calculate_frame = ttk.Frame(self.main_frame)
        calculate_frame.pack(fill=tk.X, pady=20)
        ttk.Button(calculate_frame, text="Вычислить задание 19",
                   command=self.calculate_19).pack(side=tk.LEFT, padx=5)
        ttk.Button(calculate_frame, text="Вычислить задание 20",
                   command=self.calculate_20).pack(side=tk.LEFT, padx=5)
        ttk.Button(calculate_frame, text="Вычислить задание 21",
                   command=self.calculate_21).pack(side=tk.LEFT, padx=5)
        ttk.Button(calculate_frame, text="Очистить результаты",
                   command=self.clear_results).pack(side=tk.LEFT, padx=5)

        self.results_frame = ttk.LabelFrame(self.main_frame, text="Результаты", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.results_text = tk.Text(self.results_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_operations_widgets(self, parent_frame):
        add_frame = ttk.Frame(parent_frame)
        add_frame.pack(fill=tk.X, pady=5)
        ttk.Label(add_frame, text="Добавить операцию:").pack(side=tk.LEFT)
        operation_var = tk.StringVar()
        operation_combo = ttk.Combobox(add_frame, textvariable=operation_var,
                                       values=["+3", "+6","*3", "custom"])
        operation_combo.pack(side=tk.LEFT, padx=5)
        custom_entry = ttk.Entry(add_frame, width=10)
        custom_entry.pack(side=tk.LEFT, padx=5)
        custom_entry.pack_forget()

        def on_operation_change(event):
            if operation_var.get() == "custom":
                custom_entry.pack(side=tk.LEFT, padx=5)
            else:
                custom_entry.pack_forget()

        operation_combo.bind('<<ComboboxSelected>>', on_operation_change)

        def add_operation():
            operation = operation_var.get()
            if operation == "custom":
                operation = custom_entry.get().strip()

            if operation and operation not in self.operations:
                self.operations.append(operation)
                self.update_operations_display(parent_frame)
                operation_var.set("")
                custom_entry.delete(0, tk.END)
                custom_entry.pack_forget()

        ttk.Button(add_frame, text="Добавить", command=add_operation).pack(side=tk.LEFT, padx=5)
        self.operations_display_frame = ttk.Frame(parent_frame)
        self.operations_display_frame.pack(fill=tk.X, pady=5)
        self.update_operations_display(parent_frame)

    def update_operations_display(self, parent_frame):
        for widget in self.operations_display_frame.winfo_children():
            widget.destroy()
        if self.operations:
            ttk.Label(self.operations_display_frame, text="Текущие операции:").pack(anchor=tk.W)
            operations_text = ", ".join(self.operations)
            ttk.Label(self.operations_display_frame, text=operations_text,
                      font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)

            def clear_operations():
                self.operations.clear()
                self.update_operations_display(parent_frame)

            ttk.Button(self.operations_display_frame, text="Очистить операции",
                       command=clear_operations).pack(anchor=tk.W, pady=5)
        else:
            ttk.Label(self.operations_display_frame, text="Операции не добавлены",
                      foreground="gray").pack(anchor=tk.W)

    def get_game_parameters(self):
        return {
            'heaps': int(self.heap_var.get()),
            'bad_move': self.bad_move_var.get(),
            'win_condition': self.win_condition_var.get(),
            'win_value': int(self.win_value_var.get()),
            'heap2_value': int(self.heap2.get()) if self.heap_var.get() == "2" else None,
            'operations': tuple(self.operations)  # Исправлено для lru_cache
        }

    def calculate_19(self):
        if self.calculate_19_func:
            params = self.get_game_parameters()
            result = self.calculate_19_func(params)
            self.display_result("Задание 19", result)

    def calculate_20(self):
        if self.calculate_20_func:
            params = self.get_game_parameters()
            result = self.calculate_20_func(params)
            self.display_result("Задание 20", result)

    def calculate_21(self):
        if self.calculate_21_func:
            params = self.get_game_parameters()
            result = self.calculate_21_func(params)
            self.display_result("Задание 21", result)

    def display_result(self, title, result):
        self.results_text.insert(tk.END, f"=== {title} ===\n")
        self.results_text.insert(tk.END, f"Параметры игры:\n")
        params = self.get_game_parameters()
        self.results_text.insert(tk.END, f"  Куч: {params['heaps']}\n")
        if params['heaps'] == 2:
            self.results_text.insert(tk.END, f"  Начальное значение второй кучи: {params['heap2_value']}\n")
        self.results_text.insert(tk.END, f"  Условие победы: S {params['win_condition']} {params['win_value']}\n")
        self.results_text.insert(tk.END, f"  Неудачный ход: {'да' if params['bad_move'] else 'нет'}\n")
        self.results_text.insert(tk.END, f"  Операции: {', '.join(params['operations'])}\n")
        self.results_text.insert(tk.END, f"Результат: {result}\n\n")
        self.results_text.see(tk.END)

    def clear_results(self):
        self.results_text.delete(1.0, tk.END)

    def set_calculate_functions(self, func_19, func_20, func_21):
        self.calculate_19_func = func_19
        self.calculate_20_func = func_20
        self.calculate_21_func = func_21


class Solver:
    def __init__(self):
        self.params = None

    def solve_19(self, params):
        self.params = params
        if self.params['heap2_value'] is not None:
            b = self.params['heap2_value']
        else:
            b = 0
            results = []
            if self.params['win_condition']=='>' or self.params['win_condition']=='>=':
                for i in range(1, self.params['win_value']):
                    if f(i, b, self.params['operations'], self.params['win_value'], self.params['win_condition']) == -1:
                        results.append(i)
                return f"Выигрышные позиции: {results}" if results else "Выигрышных позиций не найдено"
            else:
                for i in range(self.params['win_value'] + 1, 200):
                    if f(i, b, self.params['operations'], self.params['win_value'], self.params['win_condition']) == -1:
                        results.append(i)
                return f"Выигрышные позиции: {results}" if results else "Выигрышных позиций не найдено"

    def solve_20(self, params):
        self.params = params
        if self.params['heap2_value'] is not None:
            b = self.params['heap2_value']
        else:
            b = 0
        if not self.params['bad_move']:
            results = []
            if self.params['win_condition']=='>' or self.params['win_condition']=='>=':
                for i in range(1, self.params['win_value']):
                    if f(i, b, self.params['operations'], self.params['win_value'],self.params['win_condition']) == 2:
                        results.append(i)
                return f"Выигрышные позиции: {results}" if results else "Выигрышных позиций не найдено"
            else:
                for i in range(self.params['win_value']+1,200):
                    if f(i, b, self.params['operations'], self.params['win_value'],self.params['win_condition']) == 2:
                        results.append(i)
                return f"Выигрышные позиции: {results}" if results else "Выигрышных позиций не найдено"

    def solve_21(self, params):
        self.params = params
        if self.params['heap2_value'] is not None:
            b = self.params['heap2_value']
        else:
            b = 0
        if not self.params['bad_move']:
            results = []
            if self.params['win_condition']=='>' or self.params['win_condition']=='>=':
                for i in range(1, self.params['win_value']):
                    if f(i, b, self.params['operations'], self.params['win_value'], self.params['win_condition']) == -2:
                        results.append(i)
                return f"Выигрышные позиции: {results}" if results else "Выигрышных позиций не найдено"
            else:
                for i in range(self.params['win_value'], 200):
                    if f(i, b, self.params['operations'], self.params['win_value'], self.params['win_condition']) == -2:
                        results.append(i)
                return f"Выигрышные позиции: {results}" if results else "Выигрышных позиций не найдено"


if __name__ == "__main__":
    root = tk.Tk()
    app = EgeSolverGUI(root)
    solver = Solver()

    def calculate_19_stub(params):
        return solver.solve_19(params)

    def calculate_20_stub(params):
        return solver.solve_20(params)

    def calculate_21_stub(params):
        return solver.solve_21(params)

    app.set_calculate_functions(calculate_19_stub, calculate_20_stub, calculate_21_stub)
    root.mainloop()