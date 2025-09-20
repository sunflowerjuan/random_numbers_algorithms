import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os
import re
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
        """Carga una secuencia desde archivo CSV o TXT, intentando detectar delimitador y columna 'Ri'."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de texto o CSV", "*.txt *.csv"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            # Leer una muestra para detectar dialecto
            with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
                sample = f.read(2048)
                f.seek(0)

                # Intentar detectar dialecto con Sniffer
                delimiter = None
                has_header = False
                try:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample)
                    delimiter = dialect.delimiter
                    has_header = sniffer.has_header(sample)
                except Exception:
                    # fallback: probar delimitadores comunes
                    for d in [",", ";", "\t", "|"]:
                        f.seek(0)
                        reader = csv.reader(f, delimiter=d)
                        header = next(reader, None)
                        if header and any("ri" in (h or "").lower() for h in header):
                            delimiter = d
                            has_header = True
                            break
                    # si no encontramos un delimitador, asumimos coma y seguiremos con heurística
                    if delimiter is None:
                        delimiter = ","
                        f.seek(0)
                        has_header = csv.Sniffer().has_header(sample) if sample.strip() else False

                # Leer con el delimitador elegido
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)

                # Si detectamos encabezado, obtenerlo; si no, trabajamos las filas como datos
                header_row = None
                rows = []

                if has_header:
                    header_row = next(reader, None)

                for row in reader:
                    # Ignorar filas vacías
                    if not row or all(not cell.strip() for cell in row):
                        continue
                    rows.append(row)

                # Si no hay filas obtenidas por csv (archivo con separadores por espacios), fallback a split por línea
                if not rows:
                    f.seek(0)
                    raw_lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                    if header_row:
                        # quitar la línea de encabezado del raw_lines
                        if raw_lines:
                            raw_lines = raw_lines[1:]
                    rows = [ln.split() for ln in raw_lines if ln]

                # Normalizar encabezados y buscar 'ri'
                ri_index = None
                if header_row:
                    headers_norm = [re.sub(r"\W", "", (h or "")).lower() for h in header_row]
                    # buscar coincidencia exacta o que contenga 'ri'
                    for i, h in enumerate(headers_norm):
                        if h == "ri" or h.endswith("ri") or "ri" == h:
                            ri_index = i
                            break
                    if ri_index is None:
                        for i, h in enumerate(headers_norm):
                            if "ri" in h:
                                ri_index = i
                                break

            # Si no detectamos por encabezado, intentar detectar la columna 'Ri' por contenido
            def detect_ri_column(rows_list):
                # calcular número máximo de columnas
                max_cols = max((len(r) for r in rows_list), default=0)
                if max_cols == 0:
                    return None
                scores = [0] * max_cols
                totals = [0] * max_cols
                for r in rows_list:
                    for j in range(max_cols):
                        if j < len(r):
                            val = r[j].strip()
                            if val == "":
                                continue
                            totals[j] += 1
                            try:
                                v = float(val)
                                if 0 <= v <= 1:
                                    scores[j] += 1
                            except Exception:
                                pass
                # Elegir columna con mayor cantidad de valores válidos en [0,1]
                best = max(range(max_cols), key=lambda j: (scores[j], totals[j]))
                # Requerir al menos algún valor válido, preferentemente mayoría
                if totals[best] == 0:
                    return None
                if scores[best] >= max(1, totals[best] * 0.5):
                    return best
                if scores[best] > 0:
                    return best
                return None

            if ri_index is None:
                ri_index = detect_ri_column(rows)

            if ri_index is None:
                raise ValueError("No se pudo detectar la columna 'Ri'. Asegúrate de que el archivo tenga un encabezado 'Ri' o una columna con valores en [0,1].")

            # Extraer la columna detectada
            sequence = []
            for row in rows:
                # Manejo de filas con una sola celda (posible separación por espacios)
                if len(row) <= ri_index:
                    # intentar split por espacios si la fila está en una sola celda
                    if len(row) == 1:
                        parts = row[0].strip().split()
                        if len(parts) > ri_index:
                            candidate = parts[ri_index]
                        else:
                            continue
                    else:
                        continue
                else:
                    candidate = row[ri_index]

                candidate = candidate.strip()
                if not candidate:
                    continue
                try:
                    ri = float(candidate)
                    if not (0 <= ri <= 1):
                        # si está fuera de rango ignorarlo
                        continue
                    sequence.append(ri)
                except Exception:
                    # fila no numérica -> ignorar
                    continue

            if not sequence:
                raise ValueError("No se encontraron valores numéricos válidos en la columna detectada.")

            # Guardar estado y notificar al usuario
            self.sequence = sequence
            self.file_path = file_path
            self.file_label.config(text=f"Archivo cargado: {os.path.basename(file_path)}", fg="green")
            messagebox.showinfo("Éxito", f"Archivo cargado con {len(sequence)} valores en la columna Ri (índice detectado: {ri_index}).")

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
