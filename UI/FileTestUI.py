import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os
from UI.TestUI import TestUI


class FileTestUI(tk.Toplevel):
    """
    Ventana para cargar secuencias desde un archivo CSV/TXT o escribirlas manualmente,
    seleccionar pruebas estadísticas y luego abrir la interfaz de TestUI para ejecutarlas.
    """
    def __init__(self, parent, parent_ui=None):
        super().__init__(parent)
        self.title("Importar o Escribir Secuencia")
        self.geometry("500x800")

        # Variables internas
        self.sequence = None      # Guarda la secuencia cargada o escrita
        self.file_path = None     # Guarda ruta del archivo cargado
        self.parent_ui = parent_ui
        self.chosen_tests = []    # Lista de pruebas seleccionadas

        # Layout de la interfaz
        self._setup_layout()

        # Modal: bloquea la ventana padre hasta que esta se cierre
        if parent is not None:
            self.transient(parent)
            self.grab_set()
        parent.wait_window(self)

    def _setup_layout(self):
        """Configura todos los widgets de la interfaz."""
        frame = tk.Frame(self)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Opción 1: importar desde archivo ---
        tk.Label(frame, text="Importar desde archivo CSV/TXT (Xi, Ri)").pack(pady=5)
        btn_import = tk.Button(frame, text="Importar archivo", command=self._load_file, bg="lightblue")
        btn_import.pack(pady=5)

        # Label dinámico para mostrar nombre del archivo cargado
        self.file_label = tk.Label(frame, text="No hay archivo cargado", fg="gray")
        self.file_label.pack(pady=5)

        # --- Separador ---
        tk.Label(frame, text="O escriba los Ri manualmente (separados por coma o salto de línea):").pack(pady=5)

        # --- Opción 2: entrada manual ---
        self.text_input = tk.Text(frame, height=6, width=50)
        self.text_input.pack(pady=5)

        # Si el usuario escribe, se descarta archivo cargado
        self.text_input.bind("<KeyRelease>", self._discard_file)

        btn_submit = tk.Button(frame, text="Usar valores ingresados", command=self._load_manual, bg="lightgreen")
        btn_submit.pack(pady=5)

        # --- Selección de pruebas ---
        tk.Label(frame, text="Seleccione las pruebas a ejecutar:").pack(pady=10)

        self.test_vars = {}
        tests = ["Mean", "Variance", "Chi-Square", "Kolmogorov-Smirnov", "Poker", "Runs"]
        for t in tests:
            var = tk.BooleanVar(value=True)  # Por defecto seleccionadas
            cb = tk.Checkbutton(frame, text=t, variable=var)
            cb.pack(anchor="w")
            self.test_vars[t] = var

        # --- Botón ejecutar pruebas ---
        run_btn = tk.Button(frame, text="Ejecutar pruebas", command=self._confirm_and_open, bg="orange")
        run_btn.pack(pady=15)

        # --- Botón cerrar ---
        close_btn = tk.Button(frame, text="Cerrar", command=self.destroy, bg="lightgray")
        close_btn.pack(pady=10)

    def _confirm_and_open(self):
        """Valida selección de pruebas y existencia de secuencia antes de abrir TestUI."""
        # Guardar pruebas seleccionadas
        self.chosen_tests = [name for name, var in self.test_vars.items() if var.get()]
        if not self.chosen_tests:
            messagebox.showerror("Error", "Debe seleccionar al menos una prueba.")
            return

        if not self.sequence:
            messagebox.showerror("Error", "Debe cargar o ingresar una secuencia antes de ejecutar.")
            return

        self._open_test_ui()

    def _load_file(self):
        """Carga una secuencia desde archivo CSV o TXT, leyendo columna 'Ri'."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de texto o CSV", "*.txt *.csv"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            sequence = []
            with open(file_path, "r", newline="") as f:
                reader = csv.reader(f)

                # Leer encabezado
                header = next(reader, None)
                if not header:
                    messagebox.showerror("Error", "El archivo está vacío.")
                    return

                # Buscar índice de columna 'Ri'
                try:
                    ri_index = header.index("Ri")
                except ValueError:
                    messagebox.showerror("Error", "No se encontró la columna 'Ri' en el archivo.")
                    return

                # Leer valores de esa columna
                for row in reader:
                    if len(row) <= ri_index:
                        continue
                    try:
                        ri = float(row[ri_index])
                        if not (0 <= ri <= 1):
                            raise ValueError(f"VALORES FUERA DE RANGO Ri")
                        sequence.append(ri)
                    except ValueError as e:
                        raise ValueError(f"Valor inválido en la fila {row}: {e}")

            if not sequence:
                messagebox.showerror("Error", "No se encontraron números válidos en la columna 'Ri'.")
                return

            # Guardar secuencia y archivo cargado
            self.sequence = sequence
            self.file_path = file_path
            self.file_label.config(text=f"Archivo cargado: {os.path.basename(file_path)}", fg="green")
            messagebox.showinfo("Éxito", f"Archivo cargado con {len(sequence)} valores de la columna Ri.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

    def _load_manual(self):
        """Carga secuencia desde el cuadro de texto (manual)."""
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showerror("Error", "Debe ingresar al menos un número.")
            return

        tokens = raw_text.replace("\n", ",").split(",")
        sequence = []
        try:
            for t in tokens:
                if not t.strip():
                    continue
                val = float(t.strip())
                if not (0 <= val <= 1):
                    raise ValueError(f"VALORES FUERA DE RANGO Ri")
                sequence.append(val)

            if not sequence:
                messagebox.showerror("Error", "No se encontraron números válidos en el texto ingresado.")
                return

            # Guardar secuencia y limpiar archivo
            self.sequence = sequence
            self.file_path = None
            self.file_label.config(text="No hay archivo cargado", fg="gray")
            messagebox.showinfo("Éxito", f"Secuencia cargada con {len(sequence)} valores.")

        except Exception as e:
            messagebox.showerror("Error", f"Entrada inválida:\n{e}")

    def _discard_file(self, event=None):
        """Si el usuario escribe manualmente, descarta cualquier archivo cargado."""
        if self.text_input.get("1.0", tk.END).strip():
            if self.file_path is not None:
                self.file_path = None
                self.file_label.config(text="No hay archivo cargado", fg="gray")
                self.sequence = None

    def _open_test_ui(self):
        """Abre la ventana de TestUI con la secuencia y pruebas seleccionadas."""
        TestUI(self.master, self.sequence, chosen_tests=self.chosen_tests, parent_ui=self.parent_ui)

    def _is_numeric_row(self, row):
        """Verifica si una fila tiene un valor numérico en la segunda columna (Xi o Ri)."""
        try:
            float(row[1])
            return True
        except Exception:
            return False


def run_app():
    """Lanza la aplicación de prueba de secuencias desde archivo."""
    root = tk.Tk()
    FileTestUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
