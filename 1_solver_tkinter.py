from tkinter import *
from tkinter import ttk
from itertools import permutations
import math

class GraphDraw:
    def __init__(self, root, rows):
        self.root = root
        self.rows = rows
        self.n = len(rows)
        self.canvas = Canvas(root, width=200, height=200, bg="white")
        self.canvas.pack(pady=10)
        self.draw_graph()
    def draw_graph(self):
        radius = 50
        center_x, center_y = 100, 100
        angle_step = 2 * math.pi / self.n
        self.positions = {}
        for i in range(self.n):
            x = center_x + radius * math.cos(i * angle_step)
            y = center_y + radius * math.sin(i * angle_step)
            self.positions[i] = (x, y)
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="lightblue")
            self.canvas.create_text(x, y, text=f"{i + 1}")
        for i in range(self.n):
            for j in range(self.n):
                if self.rows[i][j] not in (0, None, '', '-'):
                    x1, y1 = self.positions[i]
                    x2, y2 = self.positions[j]
                    self.canvas.create_line(x1, y1, x2, y2)
                    if isinstance(self.rows[i][j], (int, float)):
                        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                        self.canvas.create_text(mx, my, text=str(self.rows[i][j]), fill="red")


class TableGUI:
    def __init__(self, root, rows, columns, headings):
        self.root = root
        self.rows = rows
        self.columns = columns
        self.headings = headings
        self.tree = None
    def draw(self):
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings")
        for i in range(len(self.columns)):
            self.tree.heading(self.columns[i], text=self.headings[i])
            self.tree.column(self.columns[i], width=70, anchor=CENTER)
        self.tree.pack(fill=BOTH, padx=10, pady=10)
        self.build_table()
    def build_table(self):
        for el in self.rows:
            self.tree.insert("", END, values=el)


class GraphRoad:
    def __init__(self, rows, spisok_smegnosti):
        self.rows = rows
        self.spisok_smegnosti_A = spisok_smegnosti
        self.spisok_smegnosti_1 = ""

    def adjacency_matrix_to_list(self):
        n = len(self.rows)
        parts = []
        for i in range(n):
            neighbors = []
            for j in range(n):
                if self.rows[i][j] not in (0, None, '', '-') and i != j:
                    neighbors.append(str(j + 1))
            part = str(i + 1) + ''.join(sorted(neighbors))
            parts.append(part)
        self.spisok_smegnosti_1 = ' '.join(parts)

    def EGE_solution(self):
        self.adjacency_matrix_to_list()
        s = self.spisok_smegnosti_A
        z = self.spisok_smegnosti_1
        n = len(self.rows)
        digits = ''.join(str(i + 1) for i in range(n))
        for x in permutations(set(s) - {' '}):
            t = z
            for a, b in zip(digits, x):
                t = t.replace(a, b)
            g = ' '.join(c + ''.join(sorted(v)) for c, *v in sorted(t.split()))
            s_norm = ' '.join(c + ''.join(sorted(v)) for c, *v in sorted(s.split()))
            if g == s_norm:
                return ''.join(x)
        return "Совпадений не найдено"


def input_matrix_table(root, size):
    frame = Frame(root)
    frame.pack(pady=10)
    headings = [''] + [f'Пункт {i + 1}' for i in range(size)]
    for j, h in enumerate(headings):
        Label(frame, text=h, width=8, borderwidth=1, relief="solid").grid(row=0, column=j)
    entries = []
    for i in range(size):
        row_entries = []
        Label(frame, text=f'Пункт {i + 1}', width=8, borderwidth=1, relief="solid").grid(row=i + 1, column=0)
        for j in range(size):
            e = Entry(frame, width=8, justify=CENTER)
            e.grid(row=i + 1, column=j + 1, padx=1, pady=1)
            if i == j:
                e.insert(0, "-")
            else:
                e.insert(0, "-")
            row_entries.append(e)
        entries.append(row_entries)
    return frame, entries

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Графы: матрица и список смежности")
        self.root.geometry("900x900")
        Label(root, text="Введите количество вершин:").pack(pady=5)
        self.entry_size = Entry(root, width=10, justify=CENTER)
        self.entry_size.insert(0, "7")
        self.entry_size.pack(pady=5)
        self.btn_create_table = Button(root, text="Создать таблицу для ввода", command=self.create_input_table)
        self.btn_create_table.pack(pady=5)
        self.matrix_frame = None
        self.matrix_entries = None
        self.btn_calc = None
        self.label_result = None
        self.label_spisok_smegnosti = None
        self.entry_spisok_smegnosti = None
        self.rows = None
        self.kolvo = None

    def create_input_table(self):
        size = int(self.entry_size.get())
        self.kolvo = size
        self.matrix_frame, self.matrix_entries = input_matrix_table(self.root, size)
        self.label_spisok_smegnosti = Label(self.root, text="Введите список смежности в буквах:")
        self.label_spisok_smegnosti.pack(pady=5)
        self.entry_spisok_smegnosti = Entry(self.root, width=50)
        self.entry_spisok_smegnosti.insert(0, "АБВГ БАД ВАГ ГАВДЕК ДБГ ЕГК КЕГ")
        self.entry_spisok_smegnosti.pack(pady=5)
        self.btn_calc = Button(self.root, text="Рассчитать", command=self.calc)
        self.btn_calc.pack(pady=5)
        self.label_result = Label(self.root, text="", font=("Arial", 12))
        self.label_result.pack(pady=10)

    def get_matrix_from_entries(self):
        matrix = []
        for i in range(self.kolvo):
            row = []
            for j in range(self.kolvo):
                value = self.matrix_entries[i][j].get().strip()
                if value in ('*', '-', '', 'None'):
                    row.append(None)
                else:
                    row.append(int(value))
            matrix.append(row)
        return matrix

    def calc(self):
        matrix = self.get_matrix_from_entries()
        s_spisok_smegnosti = self.entry_spisok_smegnosti.get().strip()
        display_matrix = []
        for i in range(len(matrix)):
            display_row = [f'Пункт {i + 1}'] + matrix[i]
            display_matrix.append(display_row)
        columns = tuple(["Пункт"]) + tuple(f'A{i}' for i in range(1, self.kolvo + 1))
        headings = ['Пункт'] + [f'Пункт {i}' for i in range(1, self.kolvo + 1)]
        gui = TableGUI(self.root, display_matrix, columns, headings)
        gui.draw()
        gr = GraphRoad(rows=matrix, spisok_smegnosti=s_spisok_smegnosti)
        result = gr.EGE_solution()
        self.label_result.config(text=f"Ответ: {result}")
        GraphDraw(self.root, matrix)

if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
    '''rows = [[None, None, 15, None, None, None, 20], [None, None, None, None, None, 22, 18],
    [15, None, None, None, None, None, 10], [None, None, None, None, 9, 8, None],
    [None, None, None, 9, None, None, 12], [None, 22, None, 8, None, None, 14],
    [20, 18, 10, None, 12, 14, None]]
        'АБВГ БАД ВАГ ГАВДЕК ДБГ ЕГК КЕГ'''