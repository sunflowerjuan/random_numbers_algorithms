import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog,simpledialog
import matplotlib
matplotlib.use("TkAgg")  # Se define el backend de Matplotlib para usarlo con Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

from generators.Congruences import LinealCongruence, AditiveCongruence, MultipyCongruence
from utils.export_utils import export_sequence
from UI.TestUI import TestUI
from utils.param_loader import load_param_file, filter_params


class CongruenceUI(tk.Toplevel):
    def __init__(self, parent, parent_ui=None):
        super().__init__(parent)
        self.title("Generadores de Congruencias")
        self.geometry("1000x600")

        self.sequence = []
        self.x_values = []
        self.param_sets = []  # Lista de parámetros cargados desde archivo

        self._setup_main_layout()
        self._setup_inputs()
        self._setup_buttons()
        self._setup_table()
        self._setup_status_label()
        self._setup_plot_area()

        self.update_fields()

        if parent is not None:
            self.transient(parent)
            self.grab_set()
            parent.wait_window(self)

    # ========================= SETUP UI =========================
    def _setup_main_layout(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=2)

    def _setup_inputs(self):
        self.entries = {}
        params = ["Seed", "k", "c", "g", "n"]

        tk.Label(self.left_frame, text="Método").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.method_var = tk.StringVar(value="Lineal")
        methods = ["Lineal", "Aditivo", "Multiplicativo"]
        self.method_menu = ttk.Combobox(
            self.left_frame, textvariable=self.method_var,
            values=methods, state="readonly"
        )
        self.method_menu.grid(row=0, column=1, padx=5, pady=5)
        self.method_menu.bind("<<ComboboxSelected>>", self.update_fields)

        for i, p in enumerate(params):
            tk.Label(self.left_frame, text=p).grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(self.left_frame)
            entry.grid(row=i + 1, column=1, padx=5, pady=5)
            self.entries[p] = entry

    def _setup_buttons(self):
        tk.Button(self.left_frame, text="Generar", command=self.generate).grid(row=7, column=0, pady=10)
        self.export_button = tk.Button(self.left_frame, text="Exportar", command=self.export, state="disabled")
        self.export_button.grid(row=7, column=1, pady=10)

        # Botón para cargar archivo de parámetros
        tk.Button(self.left_frame, text="Cargar Parametros", command=self.load_file).grid(row=7, column=2, pady=10)

    def _setup_table(self):
        self.table = ttk.Treeview(self.left_frame, columns=("#", "Xi", "Ri"), show="headings", height=10)
        self.table.heading("#", text="#")
        self.table.heading("Xi", text="Xi")
        self.table.heading("Ri", text="Ri")
        self.table.column("#", width=30, anchor="center")
        self.table.grid(row=8, column=0, columnspan=4, padx=5, pady=10)

    def _setup_status_label(self):
        self.hull_label = tk.Label(self.left_frame, text="Estado Hull-Dobell: ---", fg="blue")
        self.hull_label.grid(row=9, column=0, columnspan=4, pady=5)

    def _setup_plot_area(self):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Dispersión de números pseudoaleatorios")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ========================= PARAMETROS DESDE ARCHIVO =========================
    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de parámetros",
            filetypes=[("CSV o TXT", "*.csv *.txt")]
        )
        if not filepath:
            return

        try:
             # Cargar todas las filas del archivo
            rows = load_param_file(filepath)
            # Filtrar solo columnas necesarias
            self.param_sets = [filter_params(row, ["Seed","k","c","g","n"]) for row in rows]

            if not self.param_sets:
                raise ValueError("El archivo está vacío o no tiene parámetros válidos")

            if len(self.param_sets) == 1:
                self._fill_entries(self.param_sets[0])
            else:
                options = [f"Fila {i+1}: {row}" for i, row in enumerate(self.param_sets)]
                choice = self.ask_param_choice(options)
                if choice is not None:
                    self._fill_entries(self.param_sets[choice])

        except Exception as e:
            messagebox.showerror("Error", str(e))

            
            
    def ask_param_choice(self, options):
        """Abre un cuadro para elegir una fila de parámetros"""
        dialog = tk.Toplevel(self)
        dialog.title("Seleccionar configuración")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        header_label = tk.Label(dialog, text="Seed,k,c,g,n", font=("Arial", 10, "bold"))
        header_label.pack(pady=5)


        listbox = tk.Listbox(dialog, height=10)
        for opt in options:
            listbox.insert(tk.END, opt)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        chosen = {"index": None}

        def confirm():
            sel = listbox.curselection()
            if sel:
                chosen["index"] = sel[0]
                dialog.destroy()

        tk.Button(dialog, text="Aceptar", command=confirm).pack(pady=5)

        dialog.wait_window()
        return chosen["index"]

    def _fill_entries(self, param_row):
        """Llena los campos de entrada con una fila de parámetros"""
        keys = ["Seed", "k", "c", "g", "n"]
        for key in keys:
            if key in param_row:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, str(param_row[key]))

        # Detecta el método según parámetros
        seed = param_row.get("Seed", 0)
        k = param_row.get("k", 0)
        c = param_row.get("c", 0)
        g = param_row.get("g", 0)
        n = param_row.get("n", 0)

        try:
            if k == 0 and c != 0:
                self.method_var.set("Aditivo")
            elif c == 0 and k != 0:
                self.method_var.set("Multiplicativo")
            elif k != 0 and c != 0:
                self.method_var.set("Lineal")
            else:
                self.method_var.set("Lineal")  # fallback
        except Exception:
            self.method_var.set("Lineal")

        self.update_fields()



    # ========================= LÓGICA =========================
    def update_fields(self, event=None):
        """Habilita o deshabilita campos según el método elegido."""
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
        """Cambia el estado de un campo a normal o deshabilitado."""
        state = "normal" if normal else "disabled"
        self.entries[key].config(state=state)

    def _set_value(self, key, value, disable=False):
        """Asigna un valor a un campo y lo bloquea si es necesario."""
        self.entries[key].delete(0, tk.END)
        self.entries[key].insert(0, str(value))
        if disable:
            self._set_state(key, normal=False)

    def _get_inputs(self):
        """Lee los valores ingresados y valida reglas básicas."""
        try:
            seed = int(self.entries["Seed"].get())
            k = int(self.entries["k"].get())
            c = int(self.entries["c"].get())
            g = int(self.entries["g"].get())
            n = int(self.entries["n"].get())
        except ValueError:
            raise ValueError("Todos los valores deben ser enteros")

        # Validaciones básicas
        if seed % 2 == 0:
            raise ValueError("Seed (Xo) debe ser impar")
        if c % 2 == 0:
            messagebox.showwarning("Advertencia", "Se recomienda que c sea impar.")

        return seed, k, c, g, n

    def _get_generator(self, seed, k, c, g):
        """Devuelve el generador correspondiente según parámetros o menú"""
        # Autodetección
        if k == 0 and c != 0:
            self.method_var.set("Aditivo")
            return AditiveCongruence(seed, c, g)
        elif c == 0 and k != 0:
            self.method_var.set("Multiplicativo")
            return MultipyCongruence(seed, k, g)
        elif k != 0 and c != 0:
            self.method_var.set("Lineal")
            return LinealCongruence(seed, k, c, g)
        else:
            raise ValueError("Parámetros inválidos: no se puede tener k=0 y c=0 al mismo tiempo")


    def _validate_hull_dobell(self, generator, n):
        """Valida las condiciones de Hull-Dobell y muestra el estado en la etiqueta."""
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
        """Genera la secuencia, la guarda en memoria y la inserta en la tabla."""
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
        """Dibuja la dispersión de la secuencia generada en Matplotlib."""
        self.ax.clear()
        self.ax.scatter(range(len(self.sequence)), self.sequence, c="blue", marker=".")
        self.ax.set_title("Dispersión de números pseudoaleatorios")
        self.ax.set_xlabel("Índice")
        self.ax.set_ylabel("Valor Ri")
        self.ax.grid(True)
        self.canvas.draw()

    # ========================= ACCIONES =========================
    def generate(self):
        """Genera la secuencia pseudoaleatoria, valida, muestra tabla y gráfica."""
        try:
            # Obtiene parámetros
            seed, k, c, g, n = self._get_inputs()

            # Obtiene generador congruencial
            generator = self._get_generator(seed, k, c, g)

            # Valida Hull-Dobell
            self._validate_hull_dobell(generator, n)

            # Genera secuencia
            self._fill_table_and_sequence(generator, n)

            # Dibuja gráfica
            self._plot_sequence()

            # Abre ventana de pruebas estadísticas (modal)
            all_tests = ["Mean", "Variance", "Chi-Square", "Kolmogorov-Smirnov", "Poker", "Runs"]
            test_ui = TestUI(self, self.sequence, chosen_tests=all_tests, parent_ui=self)

            # Habilita o no el botón de exportar según resultado de pruebas
            if test_ui.overall_passed:
                self.export_button.config(state="normal")
            else:
                self.export_button.config(state="disabled")

        except ValueError as e:
            # Muestra error y deshabilita exportación
            messagebox.showerror("Error", str(e))
            self.export_button.config(state="disabled")

    def export(self):
        """Exporta la secuencia generada a un archivo CSV."""
        if not self.sequence:
            messagebox.showerror("Error", "Primero genere una secuencia.")
            return

        export_sequence(x_values=self.x_values, r_values=self.sequence, algorithm_name="Congruences")


def run_app():
    """Función de arranque de la aplicación principal."""
    root = tk.Tk()
    app = CongruenceUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
