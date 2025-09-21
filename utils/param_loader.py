import csv

def load_param_file(file_path):
    """
    Carga un archivo CSV/TXT con encabezados.
    Devuelve una lista de diccionarios: [{columna: valor}, ...].
    Convierte los valores a enteros cuando es posible.
    """
    rows = []
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                clean_row = {}
                for key, val in row.items():
                    if val is None or val.strip() == "":
                        continue
                    try:
                        clean_row[key.strip()] = int(val.strip())
                    except ValueError:
                        clean_row[key.strip()] = val.strip()
                rows.append(clean_row)
    except Exception as e:
        raise ValueError(f"Error al leer archivo de parámetros: {e}")
    return rows


def filter_params(row, needed_keys):
    """
    Filtra un diccionario de parámetros y devuelve solo los que interesan.
    Ej: filter_params(row, ["Seed", "n"]) → {"Seed": 7, "n": 100}
    """
    return {k: row[k] for k in needed_keys if k in row}
