import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
import csv
matplotlib.use("TkAgg")  # Usar backend de Matplotlib compatible con Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from generators.HalfSquares import HalfSquares
from utils.export_utils import export_sequence  
from UI.TestUI import TestUI  
from utils import param_loader


class HalfSquaresUI(tk.Toplevel):
    """
    Interfaz gráfica para generar y visualizar números pseudoaleatorios
    usando el método de cuadrados medios (HalfSquares).
    """
    def __init__(self, parent, parent_ui=None):
        super().__init__(parent)
        self.title("Generador - Método de Cuadrados Medios")
        self.geometry("900x600")

        # Variables
        self.sequence = []
        self.seeds = []
        self.param_sets = []  # Guardar configuraciones de archivo

        # Configuración de la interfaz
        self._setup_layout()
        self._setup_inputs()
        self._setup_buttons()
        self._setup_table()
        self._setup_plot()

        # Configuración modal si hay ventana padre
        if parent is not None:
            self.transient(parent)
            self.grab_set()
            parent.wait_window(self)

    # ========================= UI =========================
    def _setup_layout(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=2)

    def _setup_inputs(self):
        tk.Label(self.left_frame, text="Seed (X0)").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.seed_entry = tk.Entry(self.left_frame)
        self.seed_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.left_frame, text="Cantidad (n)").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.n_entry = tk.Entry(self.left_frame)
        self.n_entry.grid(row=1, column=1, padx=5, pady=5)

    def _setup_buttons(self):
        tk.Button(self.left_frame, text="Generar", command=self.generate).grid(row=2, column=0, pady=10)
        tk.Button(self.left_frame, text="Exportar", command=self._export).grid(row=2, column=1, pady=10)
        tk.Button(self.left_frame, text="Cargar parámetros", command=self.load_params).grid(row=3, column=0, columnspan=2, pady=10)

    def _setup_table(self):
        self.table = ttk.Treeview(self.left_frame, columns=("#", "Seed", "Ri"), show="headings", height=15)
        self.table.heading("#", text="#")
        self.table.heading("Seed", text="Xi")
        self.table.heading("Ri", text="Ri")
        self.table.column("#", width=30, anchor="center")
        self.table.column("Seed", width=80, anchor="center")
        self.table.column("Ri", width=100, anchor="center")
        self.table.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

    def _setup_plot(self):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Dispersión de números pseudoaleatorios")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ========================= LÓGICA =========================
    def load_params(self):
        """Carga parámetros desde archivo CSV con encabezados."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de parámetros",
            filetypes=[("CSV o TXT", "*.csv *.txt")]
        )
        if not file_path:
            return

        try:
            # Cargar todas las filas del archivo
            rows = param_loader.load_param_file(file_path)
            # Filtrar solo columnas necesarias
            self.param_sets = [param_loader.filter_params(row, ["Seed", "n"]) for row in rows]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar parámetros: {e}")
            return

        if not self.param_sets:
            messagebox.showwarning("Aviso", "No se encontraron parámetros válidos en el archivo.")
            return

        # Si hay más de una configuración, dejar que el usuario elija
        if len(self.param_sets) == 1:
            self._fill_entries(self.param_sets[0])
        else:
            options = [f"Fila {i+1}: {row}" for i, row in enumerate(self.param_sets)]
            self.ask_param_choice(options)

    def ask_param_choice(self, options):
        """Abre un cuadro para elegir configuración de parámetros."""
        dialog = tk.Toplevel(self)
        dialog.title("Seleccionar configuración")
        dialog.geometry("450x300")
        dialog.transient(self)
        dialog.grab_set()

        # Mostrar encabezado
        header_label = tk.Label(dialog, text="Encabezados: Seed, n", font=("Arial", 10, "bold"))
        header_label.pack(pady=5)

        listbox = tk.Listbox(dialog, height=10)
        for opt in options:
            listbox.insert(tk.END, opt)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        chosen = {"index": None}

        def confirm_choice():
            selection = listbox.curselection()
            if selection:
                chosen["index"] = selection[0]
                self._fill_entries(self.param_sets[chosen["index"]])
                dialog.destroy()

        tk.Button(dialog, text="Aceptar", command=confirm_choice).pack(pady=10)
        dialog.wait_window()

    def _fill_entries(self, param_dict):
        """Rellena los campos de entrada con los valores del archivo."""
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, param_dict.get("Seed", ""))

        self.n_entry.delete(0, tk.END)
        self.n_entry.insert(0, param_dict.get("n", ""))

    def generate(self):
        try:
            seed = int(self.seed_entry.get())
            n = int(self.n_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Seed y n deben ser enteros.")
            return

        if seed <= 0:
            messagebox.showerror("Error", "Seed debe ser positivo.")
            return

        if n <= 0:
            messagebox.showerror("Error", "n debe ser mayor a 0.")
            return

        generator = HalfSquares(seed, n)
        period = generator.get_period()

        if n > period:
            messagebox.showwarning(
                "Advertencia",
                f"La cantidad solicitada ({n}) es mayor al periodo ({period}). "
                f"Se generarán solo {period} números."
            )
            n = period

        self.sequence.clear()
        self.seeds.clear()
        for row in self.table.get_children():
            self.table.delete(row)

        for i in range(n):
            xi, ri = generator.next()
            self.seeds.append(xi)
            self.sequence.append(float(ri))
            self.table.insert("", "end", values=(i + 1, xi, ri))

        self._plot_sequence()

        all_tests = ["Mean", "Variance", "Chi-Square", "Kolmogorov-Smirnov", "Poker", "Runs"]
        TestUI(self, self.sequence, chosen_tests=all_tests, parent_ui=self)

    def _plot_sequence(self):
        self.ax.clear()
        self.ax.scatter(range(len(self.sequence)), self.sequence, c="blue", marker=".")
        self.ax.set_title("Dispersión de números pseudoaleatorios")
        self.ax.set_xlabel("Índice")
        self.ax.set_ylabel("Valor Ri")
        self.ax.grid(True)
        self.canvas.draw()

    def _export(self):
        if not self.sequence:
            messagebox.showerror("Error", "Primero genere una secuencia.")
            return

        export_sequence(x_values=self.seeds, r_values=self.sequence, algorithm_name="HalfSquares")


def run_app():
    root = tk.Tk()
    app = HalfSquaresUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
