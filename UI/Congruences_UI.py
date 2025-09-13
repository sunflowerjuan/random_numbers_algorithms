import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
matplotlib.use("TkAgg")  # backend para Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

from generators.Congruences import LinealCongruence, AditiveCongruence, MultipyCongruence
from utils.export_utils import export_sequence
from UI.TestUI import TestUI


class CongruenceUI:
    """
    Interfaz gráfica para generar y visualizar números pseudoaleatorios
    usando generadores congruenciales (lineal, aditivo, multiplicativo).
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Generadores de Congruencias")
        self.root.geometry("1000x600")

        self.sequence = []
        self.x_values = []

        self._setup_main_layout()
        self._setup_inputs()
        self._setup_buttons()
        self._setup_table()
        self._setup_status_label()
        self._setup_plot_area()

        self.update_fields()  # inicializa según el método por defecto

    # ========================= SETUP UI =========================
    def _setup_main_layout(self):
        """Crea la estructura de dos paneles: izquierda (inputs/tabla) y derecha (gráfica)."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=2)

    def _setup_inputs(self):
        """Crea campos de entrada y menú de selección de método."""
        self.entries = {}
        params = ["Seed", "k", "c", "g", "n"]

        # Selector de método
        tk.Label(self.left_frame, text="Método").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.method_var = tk.StringVar(value="Lineal")
        methods = ["Lineal", "Aditivo", "Multiplicativo"]
        self.method_menu = ttk.Combobox(
            self.left_frame, textvariable=self.method_var,
            values=methods, state="readonly"
        )
        self.method_menu.grid(row=0, column=1, padx=5, pady=5)
        self.method_menu.bind("<<ComboboxSelected>>", self.update_fields)

        # Entradas de parámetros
        for i, p in enumerate(params):
            tk.Label(self.left_frame, text=p).grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(self.left_frame)
            entry.grid(row=i + 1, column=1, padx=5, pady=5)
            self.entries[p] = entry

    def _setup_buttons(self):
        """Botones de generar y exportar."""
        tk.Button(self.left_frame, text="Generar", command=self.generate).grid(row=7, column=0, pady=10)
        tk.Button(self.left_frame, text="Exportar", command=self.export).grid(row=7, column=1, pady=10)

    def _setup_table(self):
        """Tabla para mostrar resultados generados."""
        self.table = ttk.Treeview(self.left_frame, columns=("#", "Xi", "Ri"), show="headings", height=10)
        self.table.heading("#", text="#")
        self.table.heading("Xi", text="Xi")
        self.table.heading("Ri", text="Ri")
        self.table.column("#", width=30, anchor="center")
        self.table.grid(row=8, column=0, columnspan=3, padx=5, pady=10)

    def _setup_status_label(self):
        """Etiqueta para mostrar validación de Hull-Dobell."""
        self.hull_label = tk.Label(self.left_frame, text="Estado Hull-Dobell: ---", fg="blue")
        self.hull_label.grid(row=9, column=0, columnspan=3, pady=5)

    def _setup_plot_area(self):
        """Área de matplotlib para graficar dispersión de resultados."""
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Dispersión de números pseudoaleatorios")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ========================= LÓGICA =========================
    def update_fields(self, event=None):
        """Habilita/deshabilita entradas según el método seleccionado."""
        method = self.method_var.get()
        if method == "Lineal":
            self._set_state("k", normal=True)
            self._set_state("c", normal=True)
        elif method == "Aditivo":
            self._set_value("k", 0, disable=True)
            self._set_state("c", normal=True)
        elif method == "Multiplicativo":
            self._set_value("c", 0, disable=True)
            self._set_state("k", normal=True)

    def _set_state(self, key, normal=False):
        """Cambia estado de un campo a normal/disabled."""
        state = "normal" if normal else "disabled"
        self.entries[key].config(state=state)

    def _set_value(self, key, value, disable=False):
        """Asigna valor a un campo y lo bloquea si es necesario."""
        self.entries[key].delete(0, tk.END)
        self.entries[key].insert(0, str(value))
        if disable:
            self._set_state(key, normal=False)

    def _get_inputs(self):
        """Lee valores de entrada y valida restricciones básicas."""
        try:
            seed = int(self.entries["Seed"].get())
            k = int(self.entries["k"].get())
            c = int(self.entries["c"].get())
            g = int(self.entries["g"].get())
            n = int(self.entries["n"].get())
        except ValueError:
            raise ValueError("Todos los valores deben ser enteros")

        if seed % 2 == 0:
            raise ValueError("Seed (Xo) debe ser impar")
        if c % 2 == 0:
            messagebox.showwarning("Advertencia", "Se recomienda que c sea impar.")

        return seed, k, c, g, n

    def _get_generator(self, seed, k, c, g):
        """Devuelve el generador correspondiente según el método."""
        method = self.method_var.get()
        if method == "Lineal":
            return LinealCongruence(seed, k, c, g)
        elif method == "Aditivo":
            return AditiveCongruence(seed, c, g)
        elif method == "Multiplicativo":
            return MultipyCongruence(seed, k, g)
        else:
            raise ValueError("Método no válido")

    def _validate_hull_dobell(self, generator, n):
        """Verifica Hull-Dobell y muestra estado en etiqueta."""
        m = generator.m
        period = generator.get_period()

        if generator.hull_dobell_validation():
            if n > m:
                raise ValueError(f"Con Hull-Dobell válido, n debe ser ≤ m ({m})")
            self.hull_label.config(text=f"Estado Hull-Dobell: CUMPLE (Periodo = {m})", fg="green")
        else:
            if n > period:
                raise ValueError(f"No cumple Hull-Dobell. n debe ser ≤ periodo ({period})")

            if period == 10**6:
                self.hull_label.config(text=f"Estado Hull-Dobell: NO CUMPLE (Periodo estimado ≥ {period})", fg="red")
            else:
                self.hull_label.config(text=f"Estado Hull-Dobell: NO CUMPLE (Periodo = {period})", fg="red")

    def _fill_table_and_sequence(self, generator, n):
        """Genera secuencia, la guarda y la inserta en la tabla."""
        self.sequence.clear()
        self.x_values.clear()
        for row in self.table.get_children():
            self.table.delete(row)

        for i in range(n):
            xi = generator.xo_seed
            ri = generator.next()
            self.sequence.append(ri)
            self.x_values.append(xi)
            self.table.insert("", "end", values=(i + 1, xi, ri))

    def _plot_sequence(self):
        """Dibuja dispersión de la secuencia en matplotlib."""
        self.ax.clear()
        self.ax.scatter(range(len(self.sequence)), self.sequence, c="blue", marker=".")
        self.ax.set_title("Dispersión de números pseudoaleatorios")
        self.ax.set_xlabel("Índice")
        self.ax.set_ylabel("Valor Ri")
        self.ax.grid(True)
        self.canvas.draw()

    # ========================= ACCIONES =========================
    def generate(self):
        """Genera la secuencia pseudoaleatoria y actualiza tabla + gráfica."""
        try:
            seed, k, c, g, n = self._get_inputs()
            generator = self._get_generator(seed, k, c, g)
            self._validate_hull_dobell(generator, n)
            self._fill_table_and_sequence(generator, n)
            self._plot_sequence()
           
           
           # Abrir ventana de pruebas
            test_win = tk.Toplevel(self.root)
            TestUI(test_win, self.sequence)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def export(self):
        """Exporta la secuencia a CSV."""
        if not self.sequence:
            messagebox.showerror("Error", "Primero genere una secuencia.")
            return

        export_sequence(x_values=self.x_values, r_values=self.sequence,algorithm_name="Congruences")


def run_app():
    root = tk.Tk()
    app = CongruenceUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()




