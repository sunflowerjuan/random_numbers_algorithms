import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
import csv

from random_numbers.generators.congruences import LinealCongruence  # tu clase en otro archivo


class LinealCongruenceUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador Congruencial Lineal")
        self.root.geometry("500x400")

        # Entradas
        self.entries = {}
        params = ["Seed", "k", "c", "g", "n"    ]
        for i, p in enumerate(params):
            tk.Label(root, text=p).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(root)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[p] = entry

        # Botones
        tk.Button(root, text="Generar", command=self.generate).grid(row=6, column=0, pady=10)
        tk.Button(root, text="Exportar", command=self.export).grid(row=6, column=1, pady=10)
        tk.Button(root, text="Graficar", command=self.plot).grid(row=6, column=2, pady=10)

        # Resultado
        self.result_text = tk.Text(root, height=10, width=60)
        self.result_text.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        self.sequence = []

    def generate(self):
        try:
            seed = int(self.entries["Seed"].get())
            k = int(self.entries["k"].get())
            c = int(self.entries["c"].get())
            g = int(self.entries["g"].get())
            n = int(self.entries["n"].get())

            generator = LinealCongruence(seed, k, c, g)
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

            self.sequence = generator.generate_sequence(n)

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Secuencia generada (n={n}):\n")
            self.result_text.insert(tk.END, ", ".join(map(str, self.sequence)))

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
                for num in self.sequence:
                    f.write(str(num) + "\n")

        elif filepath.endswith(".csv"):
            with open(filepath, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Valores"])
                for num in self.sequence:
                    writer.writerow([num])

        messagebox.showinfo("Exportación", f"Secuencia exportada en {filepath}")

    def plot(self):
        if not self.sequence:
            messagebox.showerror("Error", "Primero genere una secuencia.")
            return

        plt.plot(self.sequence, marker="o")
        plt.title("Gráfica de números pseudoaleatorios")
        plt.xlabel("Índice")
        plt.ylabel("Valor Ri")
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = LinealCongruenceUI(root)
    root.mainloop()
