from tkinter import *
from tkinter import ttk
import itertools


class Formula:
    def __init__(self, str1, el1, el2, el3, el4, result=0):
        self.str1 = str1
        self.el1 = el1
        self.el2 = el2
        self.el3 = el3
        self.el4 = el4
        self.result = result

        self.preobr()
        self.calc()

    def preobr(self):
        self.str1 = self.str1.replace('∧', ' and ')
        self.str1 = self.str1.replace('∨', ' or ')
        self.str1 = self.str1.replace('¬', ' not ')
        self.str1 = self.str1.replace('x', str(self.el1))
        self.str1 = self.str1.replace('y', str(self.el2))
        self.str1 = self.str1.replace('z', str(self.el3))
        self.str1 = self.str1.replace('w', str(self.el4))
        self.str1 = self.str1.replace('≡', ' == ')
        self.str1 = self.str1.replace('→', ' <= ')

    def calc(self):
        self.result = int(eval(self.str1))


class TruthTable:
    def __init__(self, formula_str, rows=[]):
        self.formula_str = formula_str
        self.rows = rows
        self.solution = []

    def generate_base_table(self):
        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    for w in [0, 1]:
                        formula = Formula(self.formula_str, x, y, z, w)
                        self.rows.append([x, y, z, w, formula.result])

    def EGE_solution(self):
        str_place = [[[], []] for i in range(len(self.rows))]
        xyzw_place = list(itertools.permutations(['x', 'y', 'z', 'w']))
        for k in range(len(xyzw_place)):
            for i in range(len(self.rows)):
                xyzw_znach = {'x': -1, 'y': -1, "z": -1, 'w': -1}
                empty_place = []
                for j in range(len(self.rows[i]) - 1):
                    if self.rows[i][j] != '*':
                        xyzw_znach[xyzw_place[k][j]] = int(self.rows[i][j])
                    else:
                        empty_place.append(j)
                if empty_place:
                    combinations = list(itertools.product([0, 1], repeat=len(empty_place)))
                    for comb in combinations:
                        for idx, pos in enumerate(empty_place):
                            xyzw_znach[xyzw_place[k][pos]] = comb[idx]
                        form1 = Formula(self.formula_str,xyzw_znach['x'],xyzw_znach['y'],xyzw_znach['z'],xyzw_znach['w'])
                        res = form1.result
                        if (self.rows[i][-1] == '1' and res == 1) or (self.rows[i][-1] == '0' and res == 0):
                            if xyzw_place[k] not in str_place[i][0]:
                                str_place[i][0].append(xyzw_place[k])
                                str_place[i][1].append(xyzw_znach.copy())
                else:
                    form1 = Formula(self.formula_str,xyzw_znach['x'],xyzw_znach['y'],xyzw_znach['z'],xyzw_znach['w'])
                    res = form1.result
                    if (self.rows[i][-1] == '1' and res == 1) or (self.rows[i][-1] == '0' and res == 0):
                        if xyzw_place[k] not in str_place[i][0]:
                            str_place[i][0].append(xyzw_place[k])
                            str_place[i][1].append(xyzw_znach.copy())

        for order in xyzw_place:
            valid_for_all = True
            for i in range(len(self.rows)):
                if order not in str_place[i][0]:
                    valid_for_all = False
                    break
            if valid_for_all:
                self.solution = order
                return

class TableGUI:
    def __init__(self, root, rows, columns, headings):
        self.root = root
        self.rows = rows
        self.columns = columns
        self.headings = headings
        self.is_draw = False

    def draw(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Treeview):
                widget.destroy()
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings")
        for i in range(len(self.columns)):
            self.tree.heading(self.columns[i], text=self.headings[i])
            self.tree.column(i, width=70, anchor=CENTER)
        self.tree.pack(fill=BOTH, padx=10, pady=10)
        self.build_table()
    def build_table(self):
        for el in self.rows:
            self.tree.insert("", END, values=el)

def build():
    form = entry.get()
    base_table = TruthTable(form, rows=[])
    base_table.generate_base_table()

    gui = TableGUI(root, base_table.rows, columns, headings)
    gui.draw()
    for widget in root.winfo_children():
        if isinstance(widget, Frame) and widget != entry.master:
            widget.destroy()
        elif isinstance(widget, Label) and "Ответ" in widget.cget("text"):
            widget.destroy()
    entries = input_partial_table(root)
    btn1 = ttk.Button(root, text="Узнать ответ", command=lambda: show_answer(entries))
    btn1.pack(anchor=NW, padx=6, pady=6)

def show_answer(entries):
    form = entry.get()
    rows = [[cell.get() for cell in row] for row in entries]
    truth_table = TruthTable(form, rows)
    truth_table.EGE_solution()
    for widget in root.winfo_children():
        if isinstance(widget, Label) and "Ответ" in widget.cget("text"):
            widget.destroy()
    if truth_table.solution:
        Label(root, text=f'Ответ: {"".join(truth_table.solution)}').pack()
    else:
        Label(root, text='Ответ: решение не найдено').pack()

def input_partial_table(root):
    frame = Frame(root)
    frame.pack(pady=10)
    for j, h in enumerate(headings):
        Label(frame, text=h, width=8, borderwidth=1, relief="solid").grid(row=0, column=j)
    entries = []
    for i in range(3):
        row_entries = []
        for j in range(5):
            e = Entry(frame, width=8, justify=CENTER)
            e.grid(row=i + 1, column=j, padx=1, pady=1)
            if j < 4:
                e.insert(0, "*")
            else:
                e.insert(0, "0")
            row_entries.append(e)
        entries.append(row_entries)
    return entries

if __name__ == '__main__':
    root = Tk()
    root.title("таблица истинности")
    root.geometry("900x900")
    entry = Entry(root, justify=CENTER)
    entry.insert(0, "((x ∧ ¬y) → (not z ∨ not w))∧((w→x) ∨ y)")  # 27371
    entry.pack(fill='both', padx=10, pady=10)
    columns = ("el1", "el2", "el3", "el4", "result")
    headings = ['x', 'y', 'z', 'w', 'result']
    btn = ttk.Button(root, text="Рассчитать таблицу", command=build)
    btn.pack(anchor=NW, padx=6, pady=6)
    root.mainloop()
    #truth_table.generate_base_table()
    '''formula="(x ∧ ¬y) ∨ (x ≡ z) ∨ ¬w"  '''  # 25832 answer: wzyx
    '''formula="(z ∧ y) ∨ ((x → z ) ≡ (y → w))"'''  # 15939 answer: wzyx
    '''formula="((x ∧ ¬y) → (not z ∨ not w))∧((w→x) ∨ y)"  #27371 answer: zywx '''
    '''truth_table = TruthTable(formula,[['*','*','0','0','0'],['1','1','1','0','0'],['1','0','*','*','0']]) '''  # 25832
    '''truth_table = TruthTable(formula, [['*','*','*','1','0'],['1','*','*','1','0'],['1','*','1','1','0']]) '''  # 15939