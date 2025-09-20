import tkinter as tk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from generators.test.RandomTest import RandomTestFacade 


class TestUI(tk.Toplevel):
    def __init__(self, parent, sequence, chosen_tests=None, parent_ui=None):
        super().__init__(parent)
        self.title("Resultados de Pruebas Estadísticas")
        self.geometry("1000x750")

        # Secuencia de números a evaluar
        self.sequence = sequence
        self.parent_ui = parent_ui
        self.facade = RandomTestFacade()

        # Guardar solo las pruebas seleccionadas por el usuario
        self.chosen_tests = chosen_tests if chosen_tests else []

        # Ejecuta las pruebas seleccionadas y obtiene resultados + verificación global
        self.results, self.overall_passed = self.facade.run_subset(sequence, self.chosen_tests)

        # Índice de la prueba actualmente mostrada
        self.current_test_idx = 0
    
        # Lista con nombres de las pruebas ejecutadas
        self.test_names = list(self.results.keys())

        # Configurar layout e interfaz
        self._setup_layout()
        self._show_test()

        # Configuración modal (bloquea la ventana padre hasta cerrar esta)
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def _setup_layout(self):
        # Frame principal
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Selección de nivel de significancia
        sig_frame = tk.Frame(self.main_frame)
        sig_frame.pack(pady=5)
        tk.Label(sig_frame, text="Nivel de significancia (α):", font=("Arial", 12)).pack(side="left")

        self.alpha_var = tk.StringVar(value="0.05")
        sig_menu = tk.OptionMenu(sig_frame, self.alpha_var, "0.01", "0.05", "0.10", command=self._update_alpha)
        sig_menu.pack(side="left", padx=5)

        # Nombre de la prueba actual
        self.info_label = tk.Label(self.main_frame, text="", font=("Arial", 14))
        self.info_label.pack(pady=10)

        # Frame para resultado textual e interpretación
        self.result_frame = tk.Frame(self.main_frame)
        self.result_frame.pack(fill="x", pady=10)

        # Texto explicativo/interpretación
        self.interp_label = tk.Label(self.result_frame, text="", font=("Arial", 12), wraplength=600, justify="left")
        self.interp_label.pack(side="left", padx=10, anchor="w")

        # Resultado visual PASA/NO PASA
        self.status_label = tk.Label(self.result_frame, text="", font=("Arial", 16, "bold"))
        self.status_label.pack(side="right", padx=10, anchor="e")

        # Figura para gráficas de resultados
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Botón para guardar la gráfica
        save_btn = tk.Button(self.main_frame, text="Guardar gráfica", command=self._save_plot, bg="lightblue")
        save_btn.pack(pady=5)

        # Mensaje con resultado global (todas las pruebas)
        self.global_label = tk.Label(
            self.main_frame,
            text="",
            font=("Arial", 14, "bold")
        )
        self.global_label.pack(pady=10)

        # Botones de navegación (anterior, cerrar, siguiente)
        nav_frame = tk.Frame(self.main_frame)
        nav_frame.pack(pady=10)

        self.prev_btn = tk.Button(nav_frame, text="Anterior", command=self._prev_test)
        self.prev_btn.grid(row=0, column=0, padx=10)

        self.next_btn = tk.Button(nav_frame, text="Siguiente", command=self._next_test)
        self.next_btn.grid(row=0, column=2, padx=10)

        close_btn = tk.Button(nav_frame, text="Cerrar", command=self.destroy, bg="lightgray")
        close_btn.grid(row=0, column=1, padx=10)

        # Actualiza el mensaje global
        self._update_global_label()
        
    def _save_plot(self):
        """Guardar la gráfica actual como imagen en PNG/JPG"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.fig.savefig(file_path, dpi=300)
            print(f"Gráfica guardada en {file_path}")

    def _update_alpha(self, value):
        """Reejecutar pruebas con nuevo valor de significancia (alpha)"""
        self.error = float(value)
        self.facade.set_error(self.error)
        self.results, self.overall_passed = self.facade.run_subset(self.sequence, self.chosen_tests)
        self.test_names = list(self.results.keys())
        self.current_test_idx = 0
        self._show_test()
        self._update_global_label()

    def _update_global_label(self):
        """Actualizar mensaje que indica si la secuencia pasa todas las pruebas"""
        color = "green" if self.overall_passed else "red"
        msg = "La secuencia PASA todas las pruebas." if self.overall_passed else "La secuencia NO pasa todas las pruebas."
        self.global_label.config(text=msg, fg=color)

    def _show_test(self):
        """Muestra los resultados de la prueba actual con su gráfica e interpretación"""
        test_name = self.test_names[self.current_test_idx]
        result = self.results[test_name]

        # Actualizar nombre de prueba
        self.info_label.config(text=f"Prueba: {test_name}")

        # Mostrar estado PASA/NO PASA
        color = "green" if result["passed"] == "PASA" else "red"
        self.status_label.config(text=result["passed"], fg=color)

        # Resetear figura
        self.ax.clear()
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        n = len(self.sequence)

        # --- Tipos de pruebas ---
        # Cada bloque genera la gráfica e interpretación correspondiente

        if test_name == "Mean":
            # Prueba de la media (usa distribución normal)
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
            passed = result["passed"]
            self.interp_label.config(
                text=f"La prueba de la media evalúa si la media muestral ({mean:.3f}) "
                     f"se encuentra dentro del intervalo de confianza ({li:.3f}, {ls:.3f}).\n"
                     f"Decisión: la secuencia {passed}."
            )

        elif test_name == "Variance":
            # Prueba de la varianza (usa distribución chi-cuadrado)
            from scipy.stats import chi2
            var = result["statistic"]
            li, ls = result["p_value_or_threshold"]
            df = n - 1
            x = range(0, df * 3)
            y = [chi2.pdf(val, df) for val in x]
            self.ax.plot(x, y, color="blue", label=f"Chi²(df={df})")
            self.ax.axvline(li * df, color="orange", linestyle="--", label=f"Límite inf χ²={li*df:.2f}")
            self.ax.axvline(ls * df, color="orange", linestyle="--", label=f"Límite sup χ²={ls*df:.2f}")
            self.ax.axvline(var * df, color="red", label=f"χ² observado={var*df:.2f}")
            self.ax.legend()
            self.ax.set_title("Prueba de varianza (escala χ²)")
            passed = result["passed"]
            self.interp_label.config(
                text=f"La prueba de varianza contrasta la dispersión de la secuencia.\n"
                     f"Varianza observada: {var:.4f}, límites de confianza: ({li:.4f}, {ls:.4f}).\n"
                     f"Decisión: la secuencia {passed}."
            )

        elif test_name == "Chi-Square":
            # Prueba de chi-cuadrado (frecuencias observadas vs esperadas)
            self.fig.clf()
            chi2_stat = result["statistic"]
            extra = result["p_value_or_threshold"]
            chi2_crit = extra["chi2_crit"]
            fo = extra["fo"]
            fe = extra["fe"]
            k = extra["k"]

            ax1 = self.fig.add_subplot(1, 2, 1)
            ax2 = self.fig.add_subplot(1, 2, 2)

            # Barras: frecuencias observadas vs esperadas
            x = range(k)
            width = 0.35
            ax1.bar([i - width/2 for i in x], fo, width=width, label="Observadas")
            ax1.bar([i + width/2 for i in x], fe, width=width, label="Esperadas")
            ax1.set_title(f"Chi-cuadrado: χ²={chi2_stat:.2f}, χ² crítico={chi2_crit:.2f}")
            ax1.legend()

            # Línea horizontal para χ² observado y crítico
            ax2.axhline(chi2_stat, color="red", label=f"χ²={chi2_stat:.2f}")
            ax2.axhline(chi2_crit, color="blue", linestyle="--", label=f"χ² crítico={chi2_crit:.2f}")
            ax2.set_title("Distribución de χ²")
            ax2.legend()
            self.canvas.draw()
            passed = result["passed"]
            self.interp_label.config(
                text=f"La prueba Chi-cuadrado compara frecuencias observadas y esperadas.\n"
                     f"χ² observado = {chi2_stat:.3f}, χ² crítico = {chi2_crit:.3f}.\n"
                     f"Decisión: la secuencia {passed}."
            )

        elif test_name == "Kolmogorov-Smirnov":
            # Prueba KS (comparación distribución empírica vs uniforme)
            sorted_seq = sorted(self.sequence)
            fn = [i / n for i in range(1, n + 1)]
            self.ax.plot(sorted_seq, fn, drawstyle="steps-post", label="FEC (empírica)")
            self.ax.plot(sorted_seq, sorted_seq, color="red", label="Uniforme (teórica)")
            self.ax.legend()
            self.ax.set_title("Kolmogorov-Smirnov")
            passed = result["passed"]
            self.interp_label.config(
                text=f"La prueba KS compara la distribución empírica con la uniforme(0,1).\n"
                     f"Decisión: la secuencia {passed}."
            )

        elif test_name == "Poker":
            # Prueba de Poker (clasificación de patrones de dígitos)
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
            passed = result["passed"]
            self.interp_label.config(
                text=f"La prueba Poker evalúa patrones de dígitos como pares, tercia, póker, etc.\n"
                     f"Se comparan frecuencias observadas y esperadas.\n"
                     f"Decisión: la secuencia {passed}."
            )

        elif test_name == "Runs":
            # Prueba de rachas (arriba/abajo de la mediana)
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
            passed = result["passed"]
            self.interp_label.config(
                text=f"La prueba de rachas analiza la secuencia binaria (arriba/abajo de la mediana).\n"
                     f"Número de rachas observadas: {runs}.\n"
                     f"Decisión: la secuencia {passed}."
            )
        self.canvas.draw()

    def _next_test(self):
        """Mostrar la siguiente prueba en la lista"""
        if self.current_test_idx < len(self.test_names) - 1:
            self.current_test_idx += 1
            self._show_test()

    def _prev_test(self):
        """Mostrar la prueba anterior en la lista"""
        if self.current_test_idx > 0:
            self.current_test_idx -= 1
            self._show_test()

    def all_tests_passed(self):
        """Retorna True/False dependiendo si todas las pruebas se aprobaron"""
        return self.overall_passed
