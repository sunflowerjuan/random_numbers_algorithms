import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from distributions.Distributions import NormalDistribution
from utils.export_utils import export_sequence


class NormalDistributionUI:
    """
    Interfaz gráfica para generar números con distribución normal
    usando Box-Muller y un generador congruencial lineal.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Generador - Distribución Normal")
        self.root.geometry("1000x600")

        self.r_values = []  # Uniformes Ri
        self.n_values = []  # Normales Ni

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
        labels = ["Media (μ)", "Desv. Estándar (σ)", "Seed (X0)", "Cantidad (n)"]
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
        self.table.heading("Ri", text="Ri (Uniforme)")
        self.table.heading("Ni", text="Ni (Normal)")
        self.table.column("#", width=40, anchor="center")
        self.table.column("Ri", width=100, anchor="center")
        self.table.column("Ni", width=120, anchor="center")
        self.table.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

    def _setup_plot(self):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Histograma de la Distribución Normal")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ========================= LÓGICA =========================
    def generate(self):
        try:
            mean = float(self.entries["Media (μ)"].get())
            stddev = float(self.entries["Desv. Estándar (σ)"].get())
            seed = int(self.entries["Seed (X0)"].get())
            n = int(self.entries["Cantidad (n)"].get())
        except ValueError:
            messagebox.showerror("Error", "Todos los parámetros deben ser numéricos.")
            return

        if stddev <= 0:
            messagebox.showerror("Error", "La desviación estándar debe ser positiva.")
            return
        if n <= 0:
            messagebox.showerror("Error", "n debe ser mayor a 0.")
            return

        generator = NormalDistribution(mean, stddev, seed, n)
        self.n_values = generator.generate_normal()
        # Los Ri uniformes usados se guardan en el generador
        self.r_values = generator.lcg.generate_sequence(n)[:n]

        for row in self.table.get_children():
            self.table.delete(row)

        for i, (ri, ni) in enumerate(zip(self.r_values, self.n_values)):
            self.table.insert("", "end", values=(i + 1, f"{ri:.5f}", f"{ni:.5f}"))

        self._plot_histogram()

    def _plot_histogram(self):
        """Grafica histograma de los Ni generados y la curva teórica de la Normal."""
        self.ax.clear()

        # Histograma de los datos generados
        self.ax.hist(self.n_values, bins=20, density=True, alpha=0.7, color="blue", edgecolor="black", label="Generados")

        # Calcular la curva teórica
        mean = float(self.entries["Media (μ)"].get())
        stddev = float(self.entries["Desv. Estándar (σ)"].get())

        x = np.linspace(min(self.n_values), max(self.n_values), 200)
        pdf = (1 / (stddev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / stddev) ** 2)

        # Dibujar la curva en rojo
        self.ax.plot(x, pdf, color="red", linewidth=2, label="Curva Teórica")

        self.ax.set_title("Histograma con Curva Teórica Normal")
        self.ax.set_xlabel("Valores Ni")
        self.ax.set_ylabel("Densidad")
        self.ax.legend()
        self.ax.grid(True)

        self.canvas.draw()

    def export(self):
        if not self.n_values:
            messagebox.showerror("Error", "Primero genere una secuencia.")
            return

        export_sequence(
            r_values=self.r_values,
            n_values=self.n_values,
            algorithm_name="DistribucionNormal"
        )


def run_app():
    root = tk.Tk()
    app = NormalDistributionUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
