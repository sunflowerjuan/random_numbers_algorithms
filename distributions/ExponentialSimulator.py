import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from ExponentialDistribution import ExponentialDistribution


class ExponentialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación Distribución Exponencial")

        # Variables de entrada
        self.seed_var = tk.IntVar()
        self.rate_var = tk.DoubleVar()
        self.n_var = tk.IntVar()

        self.data = None  # DataFrame de resultados

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Frame izquierdo: entradas y botones
        frame_left = tk.Frame(self.root, padx=10, pady=10)
        frame_left.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(frame_left, text="Semilla:").pack(anchor="w")
        tk.Entry(frame_left, textvariable=self.seed_var).pack(anchor="w", fill="x")

        tk.Label(frame_left, text="Tasa (λ):").pack(anchor="w")
        tk.Entry(frame_left, textvariable=self.rate_var).pack(anchor="w", fill="x")

        tk.Label(frame_left, text="Cantidad n:").pack(anchor="w")
        tk.Entry(frame_left, textvariable=self.n_var).pack(anchor="w", fill="x")

        tk.Button(frame_left, text="Generar", command=self.run_simulation).pack(pady=5, fill="x")
        tk.Button(frame_left, text="Exportar CSV", command=self.export_csv).pack(pady=5, fill="x")

        # Tabla
        self.tree = ttk.Treeview(frame_left, columns=("Index", "Ni"), show="headings", height=10)
        self.tree.heading("Index", text="Index")
        self.tree.heading("Ni", text="Ni")
        self.tree.pack(pady=10, fill="both", expand=True)

        # Frame derecho: gráfica
        self.frame_right = tk.Frame(self.root, padx=10, pady=10)
        self.frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def run_simulation(self):
        try:
            seed = self.seed_var.get()
            rate = self.rate_var.get()
            n = self.n_var.get()

            if rate <= 0 or n <= 0:
                messagebox.showerror("Error", "λ y n deben ser mayores a 0")
                return

            exp_gen = ExponentialDistribution(rate, seed, n)
            ni_values = exp_gen.generate_exponential()

            # Guardar en DataFrame
            self.data = pd.DataFrame({
                "Index": range(1, n + 1),
                "Ni": ni_values
            })

            # Mostrar en tabla
            for i in self.tree.get_children():
                self.tree.delete(i)
            for _, row in self.data.iterrows():
                self.tree.insert("", "end", values=(row["Index"], f"{row['Ni']:.4f}"))

            # Dibujar gráfica
            self.plot_histogram(rate, ni_values)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def plot_histogram(self, rate, ni_values):
        # Limpiar frame
        for widget in self.frame_right.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(ni_values, bins=30, density=True, alpha=0.6, label="Simulación")

        x = np.linspace(0, max(ni_values), 100)
        y = rate * np.exp(-rate * x)
        ax.plot(x, y, 'r-', lw=2, label="Curva teórica")

        ax.set_xlabel("x")
        ax.set_ylabel("Densidad")
        ax.set_title("Distribución Exponencial")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def export_csv(self):
        if self.data is None:
            messagebox.showerror("Error", "No hay datos para exportar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.data.to_csv(file_path, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados a {file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExponentialApp(root)
    root.mainloop()
