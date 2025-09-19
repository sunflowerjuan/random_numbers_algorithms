import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from UI.FileTestUI import FileTestUI


class MainUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Números Pseudoaleatorios y Pruebas")
        self.geometry("800x650")
        self.configure(bg="#f0f4f7")

        # --- Título ---
        title = tk.Label(
            self,
            text="NÚMEROS PSEUDOALEATORIOS\nY PRUEBAS DE NÚMEROS",
            font=("Arial", 20, "bold"),
            bg="#f0f4f7",
            fg="#2c3e50",
            pady=15
        )
        title.pack()

        # --- Imagen ---
        try:
            img = Image.open("UI/img/pseudoman.jpg")
            img = img.resize((350, 200), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(self, image=self.photo, bg="#f0f4f7")
            img_label.pack(pady=10)
        except Exception:
            tk.Label(
                self, text="(No se pudo cargar la imagen)",
                bg="#f0f4f7", fg="red"
            ).pack()

        # --- Botones de menú ---
        menu_frame = tk.Frame(self, bg="#f0f4f7")
        menu_frame.pack(pady=10)

        tk.Button(menu_frame, text="Distribuciones", font=("Arial", 14),
                  width=18, bg="#3498db", fg="white",
                  command=self._show_distributions).grid(row=0, column=0, padx=10, pady=5)

        tk.Button(menu_frame, text="Generadores", font=("Arial", 14),
                  width=18, bg="#27ae60", fg="white",
                  command=self._show_generators).grid(row=0, column=1, padx=10, pady=5)

        tk.Button(menu_frame, text="Pruebas (importar archivo)", font=("Arial", 14),
                  width=25, bg="#e67e22", fg="white",
                  command=self._show_tests).grid(row=0, column=2, padx=10, pady=5)

        # --- Contenedor para paneles ---
        self.content_frame = tk.Frame(self, bg="white", relief="solid", bd=1)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Panel inicial ---
        self._show_welcome()

        # --- Botón de salir ---
        tk.Button(self, text="Salir", font=("Arial", 12),
                  width=15, bg="#bdc3c7", command=self.quit).pack(pady=15)

    def _clear_content(self):
        """Vaciar el panel central antes de cargar otro."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_welcome(self):
        self._clear_content()
        tk.Label(
            self.content_frame,
            text="Bienvenido\nSeleccione una opción del menú superior",
            font=("Arial", 16),
            bg="white",
            fg="#2c3e50"
        ).pack(expand=True)

    def _show_distributions(self):
        self._clear_content()
        tk.Label(self.content_frame, text="Distribuciones", font=("Arial", 18, "bold"), bg="white").pack(pady=15)

        tk.Button(self.content_frame, text="Normal", width=20, height=2,
                  command=lambda: self._selected("Distribución Normal")).pack(pady=10)
        tk.Button(self.content_frame, text="Uniforme", width=20, height=2,
                  command=lambda: self._selected("Distribución Uniforme")).pack(pady=10)

    def _show_generators(self):
        self._clear_content()
        tk.Label(self.content_frame, text="Generadores", font=("Arial", 18, "bold"), bg="white").pack(pady=15)

        tk.Button(self.content_frame, text="Lineales", width=20, height=2,
                  command=lambda: self._selected("Generador Lineal")).pack(pady=10)
        tk.Button(self.content_frame, text="Cuadrados Medios", width=20, height=2,
                  command=lambda: self._selected("Generador de Cuadrados Medios")).pack(pady=10)

    def _show_tests(self):
        self._clear_content()
        tk.Label(self.content_frame, text="Pruebas", font=("Arial", 18, "bold"), bg="white").pack(pady=15)

        tk.Button(self.content_frame, text="Importar archivo Xi, Ri",
                  width=25, height=2, bg="#e67e22", fg="white",
                  command=lambda: FileTestUI(self)).pack(pady=20)

    def _selected(self, option):
        messagebox.showinfo("Selección", f"Opción seleccionada: {option}")


def run_app():
    app = MainUI()
    app.mainloop()


if __name__ == "__main__":
    run_app()
