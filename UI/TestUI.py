import tkinter as tk
from tkinter import ttk
from generators.test.RandomTest import RandomTestFacade  # asegúrate que esté en tu carpeta/librería

class TestUI(tk.Toplevel):
    def __init__(self, parent, sequence):
        super().__init__(parent)
        self.title("Pruebas de Aleatoriedad")
        self.sequence = sequence
        self.significance_var = tk.DoubleVar(value=0.05)
        self.resultado_final = None

        # --- Selección de nivel de significancia ---
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="x")
        ttk.Label(frm, text="Nivel de significancia:").pack(side="left")
        levels = [0.1, 0.05, 0.01]
        ttk.Combobox(
            frm,
            textvariable=self.significance_var,
            values=levels,
            state="readonly",
            width=5
        ).pack(side="left", padx=5)

        # Botón ejecutar
        ttk.Button(frm, text="Ejecutar pruebas", command=self.run_tests).pack(side="left", padx=10)

        # --- Tabla de resultados ---
        self.tree = ttk.Treeview(
            self,
            columns=("test", "stat", "crit", "passed"),
            show="headings",
            height=7
        )
        self.tree.heading("test", text="Prueba")
        self.tree.heading("stat", text="Estadístico")
        self.tree.heading("crit", text="Crítico / p-valor")
        self.tree.heading("passed", text="Resultado")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Mensaje final ---
        self.result_label = ttk.Label(self, text="", font=("Arial", 12, "bold"))
        self.result_label.pack(pady=5)

        # --- Modalidad ---
        self.grab_set()         # Bloquea interacción con la ventana principal
        self.transient(parent)  # Se comporta como hija de la principal
        self.wait_window(self)  # Espera a que se cierre esta ventana

    def run_tests(self):
        alpha = self.significance_var.get()
        facade = RandomTestFacade(alpha)
        results, overall_passed = facade.run_all(self.sequence)

        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insertar resultados en tabla
        for name, res in results.items():
            stat = res.get("statistic", None)
            crit = res.get("p_value_or_threshold", None)
            passed = res.get("passed", "NO PASA")

            self.tree.insert(
                "",
                "end",
                values=(
                    name,
                    round(stat, 4) if isinstance(stat, (int, float)) else stat,
                    round(crit, 4) if isinstance(crit, (int, float)) else crit,
                    passed
                ),
                tags=("ok" if passed == "PASA" else "fail",)
            )

        # Colorear filas
        self.tree.tag_configure("ok", background="#d4edda", foreground="green")   # verde
        self.tree.tag_configure("fail", background="#f8d7da", foreground="red")   # rojo

        # Mensaje final
        if overall_passed:
            self.result_label.config(text="El conjunto Ri es válido", foreground="green")
            self.resultado_final = True
        else:
            self.result_label.config(text="El conjunto Ri es RECHAZADO", foreground="red")
            self.resultado_final = False
