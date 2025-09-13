import csv
from tkinter import filedialog, messagebox
from datetime import datetime


def export_sequence(
    x_values=None,
    r_values=None,
    n_values=None,
    extra_columns=None,
    algorithm_name="Algoritmo"
):
    """
    Exporta secuencias de números pseudoaleatorios a TXT o CSV.
    
    Parámetros:
    - x_values: lista de semillas Xi
    - r_values: lista de valores Ri
    - n_values: lista de valores Ni (opcional)
    - extra_columns: dict con {"NombreColumna": lista_valores}
    - algorithm_name: nombre del algoritmo (para el nombre de archivo)
    """
    if not r_values:
        messagebox.showerror("Error", "No hay datos para exportar.")
        return

    # Asegurar listas vacías para evitar errores
    x_values = x_values or []
    n_values = n_values or []
    extra_columns = extra_columns or {}

    # Construcción del nombre de archivo por defecto
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    n_count = len(r_values)
    default_name = f"{algorithm_name}_n{n_count}_{now}.txt"

    filetypes = [("Texto", "*.txt"), ("CSV", "*.csv")]
    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=filetypes,
        initialfile=default_name
    )
    if not filepath:
        return

    # Construcción dinámica de cabeceras y filas
    headers = []
    if x_values: headers.append("Xi")
    headers.append("Ri")
    if n_values: headers.append("Ni")
    headers.extend(extra_columns.keys())

    rows = []
    for i in range(len(r_values)):
        row = []
        if x_values: row.append(x_values[i])
        row.append(f"{r_values[i]:.5f}")
        if n_values: row.append(f"{n_values[i]:.5f}")
        for col_name in extra_columns.keys():
            row.append(extra_columns[col_name][i])
        rows.append(row)

    # Escritura de archivo
    if filepath.endswith(".txt"):
        with open(filepath, "w") as f:
            f.write(", ".join(headers) + "\n")
            for row in rows:
                f.write(", ".join(map(str, row)) + "\n")
    elif filepath.endswith(".csv"):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    messagebox.showinfo("Exportación", f"Secuencia exportada en {filepath}")
