import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")  
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from distributions.Distributions import UniformDistribution
from utils.export_utils import export_sequence


class UniformDistributionUI:
    """
    Interfaz gráfica para generar números con distribución uniforme
    a partir de un generador congruencial lineal.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Generador - Distribución Uniforme")
        self.root.geometry("1000x600")

        self.sequence = []
        self.r_values = []  # valores Ri (0,1)
        self.n_values = []  # valores Ni (a,b)

        self._setup_layout()
        self._setup_inputs()
        self._setup_buttons()
        self._setup_table()
        self._setup_plot()

    # ========================= UI =========================
    def _setup_layout(self):
        self.main_frame = tk.Frame(self.root)
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

    def _setup_table(self):
        self.table = ttk.Treeview(self.left_frame, columns=("#", "Ri", "Ni"), show="headings", height=15)
        self.table.heading("#", text="#")
        self.table.heading("Ri", text="Ri")
        self.table.heading("Ni", text="Ni")
        self.table.column("#", width=40, anchor="center")
        self.table.column("Ri", width=80, anchor="center")
        self.table.column("Ni", width=100, anchor="center")
        self.table.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

    def _setup_plot(self):
        # Solo un gráfico: histograma
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Histograma de frecuencias")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ========================= LÓGICA =========================
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
        """Dibuja histograma de los valores Ni."""
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
