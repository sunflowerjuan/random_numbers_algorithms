import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
matplotlib.use("TkAgg")  
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

from distributions.Distributions import UniformDistribution
from utils.export_utils import export_sequence


class UniformDistributionUI(tk.Toplevel):
    """
    Interfaz gráfica para generar números con distribución uniforme
    a partir de un generador congruencial lineal.
    """
    def __init__(self, parent, parent_ui=None):
        super().__init__(parent)
        self.title("Generador - Distribución Uniforme")
        self.geometry("1000x600")

        self.sequence = []
        self.r_values = []  
        self.n_values = []  

        # Campos de entrada ↔ encabezados de archivo
        self.field_map = {
            "Seed (X0)": "seed",
            "Cantidad (n)": "n",
            "a": "a",
            "b": "b"
        }

        self._setup_layout()
        self._setup_inputs()
        self._setup_buttons()
        self._setup_table()
        self._setup_plot()

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
        labels = ["Seed (X0)", "Cantidad (n)", "a", "b"]
        self.entries = {}

        for i, lbl in enumerate(labels):
            tk.Label(self.left_frame, text=lbl).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(self.left_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[lbl] = entry

    def _setup_buttons(self):
        tk.Button(self.left_frame, text="Generar", command=self.generate).grid(row=4, column=0, pady=10)
        tk.Button(self.left_frame, text="Exportar", command=self.export).grid(row=4, column=1, pady=10)
        tk.Button(self.left_frame, text="Cargar Parámetros", command=self.load_params).grid(row=5, column=0, columnspan=2, pady=10)

    def _setup_table(self):
        self.table = ttk.Treeview(self.left_frame, columns=("#", "Ri", "Ni"), show="headings", height=15)
        self.table.heading("#", text="#")
        self.table.heading("Ri", text="Ri")
        self.table.heading("Ni", text="Ni")
        self.table.column("#", width=40, anchor="center")
        self.table.column("Ri", width=80, anchor="center")
        self.table.column("Ni", width=100, anchor="center")
        self.table.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

    def _setup_plot(self):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Histograma de frecuencias")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ========================= LÓGICA =========================
    def load_params(self):
        """Cargar parámetros desde un archivo CSV/TXT con encabezados."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de parámetros",
            filetypes=[("Archivos CSV/TXT", "*.csv *.txt"), ("Todos", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                messagebox.showerror("Error", "El archivo no contiene datos.")
                return

            if len(rows) > 1:
                options = [f"Fila {i+1}: {row}" for i, row in enumerate(rows)]
                choice = self.ask_param_choice(options)
                if choice is None:
                    return
                row = rows[choice]
            else:
                row = rows[0]

            # Llenar los campos
            for label, key in self.field_map.items():
                if key in row and row[key].strip():
                    self.entries[label].delete(0, tk.END)
                    self.entries[label].insert(0, row[key])

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar parámetros: {e}")

    def ask_param_choice(self, options):
        dialog = tk.Toplevel(self)
        dialog.title("Seleccionar configuración")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        label = tk.Label(dialog, text="Seleccione una configuración de parámetros:")
        label.pack(pady=5)

        listbox = tk.Listbox(dialog, height=10)
        for opt in options:
            listbox.insert(tk.END, opt)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        chosen = {"index": None}

        def confirm():
            selection = listbox.curselection()
            if selection:
                chosen["index"] = selection[0]
                dialog.destroy()

        tk.Button(dialog, text="Aceptar", command=confirm).pack(pady=10)

        self.wait_window(dialog)
        return chosen["index"]

    def generate(self):
        try:
            seed = int(self.entries["Seed (X0)"].get())
            n = int(self.entries["Cantidad (n)"].get())
            a = float(self.entries["a"].get())
            b = float(self.entries["b"].get())
        except ValueError:
            messagebox.showerror("Error", "Los parámetros deben ser numéricos.")
            return

        if n <= 0:
            messagebox.showerror("Error", "n debe ser mayor a 0.")
            return
        if b <= a:
            messagebox.showerror("Error", "Se requiere que b > a.")
            return

        generator = UniformDistribution(seed, n, a, b)
        self.r_values = generator.lcg.generate_sequence(n)
        self.n_values = generator.generate_uniform()

        self.sequence.clear()
        for row in self.table.get_children():
            self.table.delete(row)

        for i, (ri, ni) in enumerate(zip(self.r_values, self.n_values)):
            self.table.insert("", "end", values=(i + 1, f"{ri:.5f}", f"{ni:.5f}"))

        self._plot_sequence()

    def _plot_sequence(self):
        self.ax.clear()
        self.ax.hist(self.n_values, bins=20, density=True, alpha=0.7,
                    color="green", edgecolor="black")
        self.ax.set_title("Histograma de frecuencias")
        self.ax.set_xlabel("Valores Ni")
        self.ax.set_ylabel("Densidad")
        self.ax.grid(True)
        self.canvas.draw()

    def export(self):
        if not self.n_values:
            messagebox.showerror("Error", "Primero genere una secuencia.")
            return

        export_sequence(
            r_values=self.r_values,
            n_values=self.n_values,
            algorithm_name="DistribucionUniforme"
        )


def run_app():
    root = tk.Tk()
    app = UniformDistributionUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
