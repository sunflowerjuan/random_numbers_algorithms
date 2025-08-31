# Random Numbers Algorithms

This project provides implementations of various random number generators. It is organized into modular components for easy integration and testing.

## Project Structure

- `random_numbers/`
  - `generators/` — Contains different random number generator implementations.

## Exponential Distribution Simulator

El proyecto incluye un simulador de la distribución exponencial implementado en [ExponentialDistribution.py](distributions/ExponentialDistribution.py)
y su interfaz gráfica en [ExponentialSimulador.py.](distributions/ExponentialSimulator.py)

### Requisitos

Antes de ejecutar el simulador, asegúrate de tener instalado, Python 3.8+ con las siguientes librerias

- matplotlib
- pandas
- numpy
  que puede instalar con el siguiente comando

```
pip install matplotlib pandas numpy
```

### Cómo correr el simulador

1. Clona el repositorio:

```bash
git clone https://github.com/sunflowerjuan/random_numbers_algorithms
```

2. Ingresa al directorio root del proyecto:

```bash
cd random_numbers_algorithms
```

3. Ejecuta la aplicación gráfica:

```bash
python ExponentialSimulator.py
```

4. En la interfaz del simulador:

- Ingresa la semilla (Seed).

- Define el valor de λ (tasa).

- Indica la cantidad n de números a generar.

- Haz clic en Generar.

Verás:

- Una tabla con los valores 𝑅𝑖 y 𝑁𝑖

- Un histograma con la curva teórica de la distribución exponencial.

Opcionalmente, puedes exportar los datos a CSV.

## License

This project is licensed under the MIT
