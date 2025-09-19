import tkinter as tk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from generators.test.RandomTest import RandomTestFacade  # tu fachada de pruebas


class TestUI(tk.Toplevel):  # ahora es modal
    def __init__(self, parent, sequence, parent_ui=None):
        super().__init__(parent)
        self.title("Pruebas Estadísticas")
        self.geometry("950x750")  # más alto para dar espacio

        self.sequence = sequence
        self.error = 0.05  # default
        self.facade = RandomTestFacade(error=self.error)

        # Ejecutar pruebas iniciales
        self.results, self.overall_passed = self.facade.run_all(self.sequence)
        self.test_names = list(self.results.keys())
        self.index = 0

        # Layout
        self._setup_layout()
        self._show_test()

        # Modal
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def _setup_layout(self):
        # Frame principal
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Selección de significancia
        sig_frame = tk.Frame(self.main_frame)
        sig_frame.pack(pady=5)
        tk.Label(sig_frame, text="Nivel de significancia (α):", font=("Arial", 12)).pack(side="left")

        self.alpha_var = tk.StringVar(value="0.05")
        sig_menu = tk.OptionMenu(sig_frame, self.alpha_var, "0.01", "0.05", "0.10", command=self._update_alpha)
        sig_menu.pack(side="left", padx=5)

        # Info de prueba
        self.info_label = tk.Label(self.main_frame, text="", font=("Arial", 14))
        self.info_label.pack(pady=10)

        # Resultado PASA/NO PASA
        self.status_label = tk.Label(self.main_frame, text="", font=("Arial", 16, "bold"))
        self.status_label.pack(pady=5)

        # Figura matplotlib
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # --- Botón de guardar gráfica ---
        save_btn = tk.Button(self.main_frame, text="Guardar gráfica", command=self._save_plot, bg="lightblue")
        save_btn.pack(pady=5)

        # Label con resultado global
        self.global_label = tk.Label(
            self.main_frame,
            text="",
            font=("Arial", 14, "bold")
        )
        self.global_label.pack(pady=10)

        # Botones de navegación
        nav_frame = tk.Frame(self.main_frame)
        nav_frame.pack(pady=10)

        self.prev_btn = tk.Button(nav_frame, text="Anterior", command=self._prev_test)
        self.prev_btn.grid(row=0, column=0, padx=10)

        self.next_btn = tk.Button(nav_frame, text="Siguiente", command=self._next_test)
        self.next_btn.grid(row=0, column=1, padx=10)

        # Botón de cerrar
        close_btn = tk.Button(self.main_frame, text="Cerrar", command=self.destroy, bg="lightgray")
        close_btn.pack(pady=15)

        # Actualiza label global
        self._update_global_label()
        
    def _save_plot(self):
        """Guardar la gráfica actual como imagen"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.fig.savefig(file_path, dpi=300)
            print(f"Gráfica guardada en {file_path}")

    def _update_alpha(self, value):
        """Reejecutar pruebas con nuevo alpha"""
        self.error = float(value)
        self.facade.set_error(self.error)
        self.results, self.overall_passed = self.facade.run_all(self.sequence)
        self.test_names = list(self.results.keys())
        self.index = 0
        self._show_test()
        self._update_global_label()

    def _update_global_label(self):
        color = "green" if self.overall_passed else "red"
        msg = "La secuencia PASA todas las pruebas." if self.overall_passed else "La secuencia NO pasa todas las pruebas."
        self.global_label.config(text=msg, fg=color)

    def _show_test(self):
        test_name = self.test_names[self.index]
        result = self.results[test_name]

        self.info_label.config(text=f"Prueba: {test_name}")
        color = "green" if result["passed"] == "PASA" else "red"
        self.status_label.config(text=result["passed"], fg=color)

        # --- Gráfica ---
        self.ax.clear()
        n = len(self.sequence)

        if test_name == "Mean":
            from scipy.stats import norm
            mean = result["statistic"]
            li, ls = result["p_value_or_threshold"]
            mu = 0.5
            sigma = (1 / (12 * n)) ** 0.5
            x = [mu + (i - 50) / 200 for i in range(100)]
            y = [norm.pdf(val, mu, sigma) for val in x]
            self.ax.plot(x, y, color="blue", label="Distribución Normal(0.5, σ²/n)")
            self.ax.axvline(li, color="orange", linestyle="--", label=f"Límite inf={li:.3f}")
            self.ax.axvline(ls, color="orange", linestyle="--", label=f"Límite sup={ls:.3f}")
            self.ax.axvline(mean, color="red", label=f"Media real={mean:.3f}")
            self.ax.legend()
            self.ax.set_title("Intervalo de confianza de la media")

        elif test_name == "Variance":
            from scipy.stats import chi2
            var = result["statistic"]
            li, ls = result["p_value_or_threshold"]
            df = n - 1
            x = range(0, df * 3)
            y = [chi2.pdf(val, df) for val in x]
            self.ax.plot(x, y, color="blue", label=f"Chi²(df={df})")
            self.ax.axvline(li, color="orange", linestyle="--", label=f"Límite inf={li:.3f}")
            self.ax.axvline(ls, color="orange", linestyle="--", label=f"Límite sup={ls:.3f}")
            self.ax.axvline(var * (n - 1), color="red", label=f"χ² observado={var * (n - 1):.2f}")
            self.ax.legend()
            self.ax.set_title("Intervalo de confianza de la varianza")

        elif test_name == "Chi-Square":
            chi2_stat = result["statistic"]
            chi2_crit = result["p_value_or_threshold"]
            self.ax.hist(self.sequence, bins=10, edgecolor="black", density=True)
            self.ax.axhline(chi2_stat, color="red", label=f"χ²={chi2_stat:.2f}")
            self.ax.axhline(chi2_crit, color="blue", linestyle="--", label=f"χ² crítico={chi2_crit:.2f}")
            self.ax.legend()
            self.ax.set_title("Chi-cuadrado (frecuencias observadas vs esperadas)")

        elif test_name == "Kolmogorov-Smirnov":
            sorted_seq = sorted(self.sequence)
            fn = [i / n for i in range(1, n + 1)]
            self.ax.plot(sorted_seq, fn, drawstyle="steps-post", label="FEC (empírica)")
            self.ax.plot(sorted_seq, sorted_seq, color="red", label="Uniforme (teórica)")
            self.ax.legend()
            self.ax.set_title("Kolmogorov-Smirnov")

        elif test_name == "Poker":
            obs = result["statistic"]
            exp = result["p_value_or_threshold"]
            categorias = ["Diferentes", "Par", "2 Pares", "Tercia", "Full", "Poker", "Quintilla"]
            x = range(len(categorias))
            self.ax.bar([i - 0.2 for i in x], obs, width=0.4, label="Observadas")
            self.ax.bar([i + 0.2 for i in x], exp, width=0.4, label="Esperadas")
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(categorias, rotation=30)
            self.ax.legend()
            total_obs = sum(obs)
            self.ax.text(
                0.5, -0.25,
                f"Total manos: {total_obs} | Decisión final: {result['passed']}",
                transform=self.ax.transAxes,
                ha="center", fontsize=11, color=color
            )
            self.ax.set_ylabel("Frecuencia")
            self.ax.set_title("Poker Test: Clasificación y frecuencias")

        elif test_name == "Runs":
            seq = [1 if x > 0.5 else 0 for x in self.sequence]
            self.ax.plot(seq, marker="o", linestyle="-", label="Secuencia binaria")
            self.ax.axhline(0.5, color="orange", linestyle="--", label="Mediana = 0.5")
            runs = 1
            for i in range(1, len(seq)):
                if seq[i] != seq[i - 1]:
                    runs += 1
            self.ax.text(
                0.5, -0.15,
                f"Número de rachas observadas: {runs}",
                transform=self.ax.transAxes,
                ha="center", fontsize=11
            )
            self.ax.legend()
            self.ax.set_title("Runs Test (rachas arriba/abajo de la mediana)")

        self.canvas.draw()

    def _next_test(self):
        if self.index < len(self.test_names) - 1:
            self.index += 1
            self._show_test()

    def _prev_test(self):
        if self.index > 0:
            self.index -= 1
            self._show_test()
    
    def all_tests_passed(self):
        return self.overall_passed

