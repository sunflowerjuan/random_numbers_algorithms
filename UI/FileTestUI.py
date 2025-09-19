import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from UI.TestUI import TestUI


class FileTestUI(tk.Toplevel):
    def __init__(self, parent, parent_ui=None):
        super().__init__(parent)
        self.title("Importar Secuencia desde archivo")
        self.geometry("400x200")

        self.sequence = None
        self.parent_ui = parent_ui

        # Layout
        self._setup_layout()

        # Modal solo si el parent no es root
        if parent is not None:
            self.transient(parent)
            self.grab_set()
            parent.wait_window(self)

    def _setup_layout(self):
        frame = tk.Frame(self)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="Seleccione un archivo CSV o TXT con columnas Xi, Ri").pack(pady=10)

        btn_import = tk.Button(frame, text="Importar archivo", command=self._load_file, bg="lightblue")
        btn_import.pack(pady=10)

        close_btn = tk.Button(frame, text="Cerrar", command=self.destroy, bg="lightgray")
        close_btn.pack(pady=10)

    def _load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de texto o CSV", "*.txt *.csv"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            sequence = []
            with open(file_path, "r", newline="") as f:
                reader = csv.reader(f)
                # Intenta saltar encabezado si existe
                first_row = next(reader, None)
                if first_row and not self._is_numeric_row(first_row):
                    # Si la primera fila no es numérica, asumimos que es encabezado
                    pass
                else:
                    # Si sí era numérica, la añadimos
                    if first_row and len(first_row) >= 2:
                        try:
                            sequence.append(float(first_row[1]))
                        except ValueError:
                            pass

                # Procesamos el resto
                for row in reader:
                    if len(row) < 2:
                        continue
                    try:
                        ri = float(row[1])  # segunda columna
                        sequence.append(ri)
                    except ValueError:
                        continue

            if not sequence:
                messagebox.showerror("Error", "No se encontraron números válidos en el archivo.")
                return

            self.sequence = sequence
            # Abrimos TestUI con la secuencia cargada
            TestUI(self.master, self.sequence, parent_ui=self.parent_ui)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

    def _is_numeric_row(self, row):
        """Verifica si una fila del archivo contiene datos numéricos en la segunda columna"""
        try:
            float(row[1])
            return True
        except Exception:
            return False


def run_app():
    root = tk.Tk()
    FileTestUI(root)  # Ventana de importación
    root.mainloop()


if __name__ == "__main__":
    run_app()
