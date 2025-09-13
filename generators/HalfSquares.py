class HalfSquares:
    
    def __init__(self, seed, n):
        self.seed = seed
        self.n = n
        self.sequence = []

    def _truncate(self, value, decimals=5):
        """Trunca un número flotante a la cantidad de decimales indicada."""
        factor = 10 ** decimals
        return int(value * factor) / factor

    def next(self):
        """
        Genera el siguiente número usando el método de cuadrados medios.
        Devuelve:
            xi -> Xi como string de 4 dígitos relleno con ceros si se necesita.
            ri -> Ri truncado a 5 decimales como string.
        """
        # Elevar al cuadrado y asegurar los 8 dígitos
        x_squared = str(self.seed ** 2).zfill(8)

        # Tomar los 4 dígitos del medio
        mid_digits = x_squared[2:6]
        xi = mid_digits  # Xi   con 4 dígitos
        self.seed = int(mid_digits)

        # Normalizar y truncar a 5 decimales
        ri = self._truncate(self.seed / 10000, 5)

        return xi, f"{ri:.5f}"

    def get_period(self, max_limit=100000):
        """
        Calcula el periodo antes de repetirse o llegar a 0.
        max_limit evita ciclos infinitos (por defecto 100000).
        """
        seen = set()
        count = 0
        temp_seed = self.seed

        while count < max_limit:
            if temp_seed in seen or temp_seed == 0:
                break
            seen.add(temp_seed)
            x_squared = str(temp_seed ** 2).zfill(8)
            temp_seed = int(x_squared[2:6])
            count += 1

        return count
