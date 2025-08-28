import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
matplotlib.use("TkAgg")  # backend para Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

from Congruences import LinealCongruence, AditiveCongruence, MultipyCongruence


class CongruenceUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Generadores de Congruencias")
        self.root.geometry("1000x600")  # más ancha para que quepa tabla + gráfica

        # Marco principal dividido en dos columnas
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # Panel izquierdo (inputs + tabla)
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Panel derecho (gráfica)
        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)  # derecha más grande

        # ====== Inputs ======
        self.entries = {}
        params = ["Seed", "k", "c", "g", "n"]
        for i, p in enumerate(params):
            tk.Label(left_frame, text=p).grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(left_frame)
            entry.grid(row=i + 1, column=1, padx=5, pady=5)
            self.entries[p] = entry

        # Menú selección método
        tk.Label(left_frame, text="Método").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.method_var = tk.StringVar(value="Lineal")
        methods = ["Lineal", "Aditivo", "Multiplicativo"]
        self.method_menu = ttk.Combobox(left_frame, textvariable=self.method_var, values=methods, state="readonly")
        self.method_menu.grid(row=0, column=1, padx=5, pady=5)
        self.method_menu.bind("<<ComboboxSelected>>", self.update_fields)

        # Botones
        tk.Button(left_frame, text="Generar", command=self.generate).grid(row=7, column=0, pady=10)
        tk.Button(left_frame, text="Exportar", command=self.export).grid(row=7, column=1, pady=10)
        tk.Button(left_frame, text="Graficar", command=self.plot).grid(row=7, column=2, pady=10)

        # Tabla resultados
        self.table = ttk.Treeview(left_frame, columns=("#", "Xi", "Ri"), show="headings", height=10)
        self.table.heading("#", text="#")
        self.table.heading("Xi", text="Xi")
        self.table.heading("Ri", text="Ri")
        self.table.column("#", width=30, anchor="center")  # ancho pequeño
        self.table.grid(row=8, column=0, columnspan=3, padx=5, pady=10)

        # ====== Área de gráfica ======
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Dispersión de números pseudoaleatorios")

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.sequence = []
        self.x_values = []

        self.update_fields()

    def update_fields(self, event=None):
        method = self.method_var.get()
        if method == "Lineal":
            self.entries["k"].config(state="normal")
            self.entries["c"].config(state="normal")
        elif method == "Aditivo":
            self.entries["k"].delete(0, tk.END)
            self.entries["k"].insert(0, "0")
            self.entries["k"].config(state="disabled")
            self.entries["c"].config(state="normal")
        elif method == "Multiplicativo":
            self.entries["c"].delete(0, tk.END)
            self.entries["c"].insert(0, "0")
            self.entries["c"].config(state="disabled")
            self.entries["k"].config(state="normal")

    def generate(self):
        try:
            seed = int(self.entries["Seed"].get())
            k = int(self.entries["k"].get())
            c = int(self.entries["c"].get())
            g = int(self.entries["g"].get())
            n = int(self.entries["n"].get())

            method = self.method_var.get()
            if method == "Lineal":
                generator = LinealCongruence(seed, k, c, g)
            elif method == "Aditivo":
                generator = AditiveCongruence(seed, c, g)
            elif method == "Multiplicativo":
                generator = MultipyCongruence(seed, k, g)
            else:
                raise ValueError("Método no válido")

            m = generator.m
            period = generator.get_period()

            if generator.hull_dobell_validation():
                if n > m:
                    messagebox.showerror("Error", f"Con Hull-Dobell válido, n debe ser ≤ m ({m})")
                    return
                else:
                    messagebox.showinfo("Hull-Dobell", "¡Felicidades! Cumple con Hull-Dobell.")
            else:
                if n > period:
                    messagebox.showerror("Error", f"No cumple Hull-Dobell. n debe ser ≤ periodo ({period})")
                    return

            self.sequence = []
            self.x_values = []
            for row in self.table.get_children():
                self.table.delete(row)

            for i in range(n):
                xi = generator.xo_seed
                ri = generator.next()   
                self.sequence.append(ri)
                self.x_values.append(xi)
                # i+1 será el número de fila (contador)
                self.table.insert("", "end", values=(i + 1, xi, ri))


        except ValueError:
            messagebox.showerror("Error", "Verifique que todos los valores sean números enteros.")

    def export(self):
        if not self.sequence:
            messagebox.showerror("Error", "Primero genere una secuencia.")
            return

        filetypes = [("Texto", "*.txt"), ("CSV", "*.csv")]
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)

        if filepath.endswith(".txt"):
            with open(filepath, "w") as f:
                for xi, ri in zip(self.x_values, self.sequence):
                    f.write(f"{xi}, {ri}\n")
        elif filepath.endswith(".csv"):
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Xi", "Ri"])
                for xi, ri in zip(self.x_values, self.sequence):
                    writer.writerow([xi, ri])

        messagebox.showinfo("Exportación", f"Secuencia exportada en {filepath}")

    def plot(self):
        if not self.sequence:
            messagebox.showerror("Error", "Primero genere una secuencia.")
            return

        # limpiar gráfico anterior
        self.ax.clear()
        self.ax.scatter(range(len(self.sequence)), self.sequence, c="blue", marker="o")
        self.ax.set_title("Dispersión de números pseudoaleatorios")
        self.ax.set_xlabel("Índice")
        self.ax.set_ylabel("Valor Ri")
        self.ax.grid(True)
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = CongruenceUI(root)
    root.mainloop()
