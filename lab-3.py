import tkinter as tk
from tkinter import ttk, messagebox
import time

class RasterizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Растровые алгоритмы")
        WIDTH = 600
        HEIGHT = 600
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.pack()

        # Начальные параметры
        self.scale = 20
        self.grid_color = "lightgray"
        self.axis_color = "black"
        self.line_color = "blue"

        self.pixel_size = 1
        # Смещение начала координат
        self.offset_x = 0
        self.offset_y = 0
        self.x0 = 0
        self.y0 = 0
        # Список для хранения нарисованных линий и окружностей (относительно начала координат)
        self.shapes = []

        # Интерфейс для выбора алгоритма и ввода координат
        control_frame = tk.Frame(root)
        control_frame.pack()

        tk.Label(control_frame, text="Алгоритм:").grid(row=0, column=0)
        self.algorithm_choice = ttk.Combobox(control_frame, values=["Пошаговый", "ЦДА", "Брезенхем", "Брезенхем (окружность)"])
        self.algorithm_choice.current(0)
        self.algorithm_choice.grid(row=0, column=1)

        tk.Label(control_frame, text="Начало (X1, Y1):").grid(row=1, column=0)
        self.x1_entry = tk.Entry(control_frame, width=5)
        self.x1_entry.grid(row=1, column=1)
        self.y1_entry = tk.Entry(control_frame, width=5)
        self.y1_entry.grid(row=1, column=2)

        tk.Label(control_frame, text="Конец (X2, Y2) / Радиус:").grid(row=2, column=0)
        self.x2_entry = tk.Entry(control_frame, width=5)
        self.x2_entry.grid(row=2, column=1)
        self.y2_entry = tk.Entry(control_frame, width=5)
        self.y2_entry.grid(row=2, column=2)

        tk.Label(control_frame, text="Масштаб:").grid(row=3, column=0)
        self.scale_entry = tk.Entry(control_frame, width=5)
        self.scale_entry.insert(0, str(self.scale))
        self.scale_entry.grid(row=3, column=1)

        draw_button = tk.Button(control_frame, text="Нарисовать", command=self.draw)
        draw_button.grid(row=4, column=0, columnspan=3)

        self.move_frame = tk.Frame(self.root)
        self.left_button = tk.Button(self.move_frame, text="<", command=self.move_left)
        self.left_button.grid(row=1, column=0)
        self.right_button = tk.Button(self.move_frame, text=">", command=self.move_right)
        self.right_button.grid(row=1, column=2)
        self.up_button = tk.Button(self.move_frame, text='/\\', command=self.move_up)
        self.up_button.grid(row=0, column=1)
        self.down_button = tk.Button(self.move_frame, text='\\/', command=self.move_down)
        self.down_button.grid(row=1, column=1)
        self.move_frame.pack()

        self.time_text_var = tk.StringVar(self.root, 'Execution time will be here')
        self.time_label = tk.Label(self.root, textvariable=self.time_text_var)
        self.time_label.pack()
        self.clean_button = tk.Button(self.root, text="clean", command=self.clear_all)
        self.clean_button.pack()
        # Привязка событий клавиатуры
#        self.root.bind("<Left>", self.move_left)
#        self.root.bind("<Right>", self.move_right)
#        self.root.bind("<Up>", self.move_up)
#        self.root.bind("<Down>", self.move_down)

        self.x0 = WIDTH // 2
        self.y0 = HEIGHT // 2

        # Нарисовать координатную плоскость
        self.draw_grid()

    def draw_grid(self):
        """Отрисовка координатной плоскости с осями и сеткой."""
        self.canvas.delete("grid")
        self.canvas.delete("axes")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        

        # Рисование сетки с учетом смещения начала координат
        for x in range(0, width, self.scale):
            self.canvas.create_line(x, 0, x, height, fill=self.grid_color, tags="grid")
        for y in range(0, height, self.scale):
            self.canvas.create_line(0, y, width, y, fill=self.grid_color, tags="grid")

        # Оси X и Y с учетом смещения
        center_x = self.x0
        center_y = self.y0
        self.canvas.create_line(center_x, 0, center_x, height, fill=self.axis_color, width=2, tags="axes")
        self.canvas.create_line(0, center_y, width, center_y, fill=self.axis_color, width=2, tags="axes")

        # Перерисовка всех фигур
        self.redraw_shapes()

    def redraw_shapes(self):
        """Перерисовка всех нарисованных фигур с учетом смещения начала координат."""
        for shape in self.shapes:
            if shape['type'] == 'line':
                self.bresenham(shape['x1'], shape['y1'], shape['x2'], shape['y2'], draw=True)
            elif shape['type'] == 'circle':
                self.bresenham_circle(shape['xc'], shape['yc'], shape['radius'], draw=True)

    def draw(self):
        """Основной метод для вызова выбранного алгоритма."""
        # Получение начальных данных
        try:
            #относительные координаты
            x1 = int(self.x1_entry.get())
            y1 = int(self.y1_entry.get())
            x2 = int(self.x2_entry.get())
            y2 = int(self.y2_entry.get())
            scale = int(self.scale_entry.get())
            
            self.canvas.delete("line")
            self.scale = scale
            self.draw_grid()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения.")
            return

        # Выбор алгоритма
        algorithm = self.algorithm_choice.get()
        if algorithm == "Пошаговый":
            self.add_shape('line', x1, y1, x2, y2)
            start = time.time() 
            self.step_by_step(x1, y1, x2, y2)
            end = time.time()
        elif algorithm == "ЦДА":
            self.add_shape('line', x1, y1, x2, y2)
            start = time.time()
            self.dda(x1, y1, x2, y2)
            end = time.time()
        elif algorithm == "Брезенхем":
            self.add_shape('line', x1, y1, x2, y2)
            start = time.time()
            self.bresenham(x1, y1, x2, y2, draw=True)
            end = time.time()
        elif algorithm == "Брезенхем (окружность)":
            radius = abs(x2)  # Радиус передается через X2
            self.add_shape('circle', x1, y1, radius)
            start = time.time()
            self.bresenham_circle(x1, y1, radius)
            end = time.time()

        else:
            messagebox.showwarning("Ошибка", "Выберите корректный алгоритм.")
        
        self.time_text_var.set('Time of operation: {:.5f} ms'.format(end - start))
        #self.time_label.update()

    def add_shape(self, shape_type, *args):
        """Добавление новой фигуры в список (сохранение относительно начала координат)."""
        if shape_type == 'line':
            self.shapes.append({'type': 'line', 'x1': args[0], 'y1': args[1], 'x2': args[2], 'y2': args[3]})
        elif shape_type == 'circle':
            self.shapes.append({'type': 'circle', 'xc': args[0], 'yc': args[1], 'radius': args[2]})

    def to_canvas_coords(self, x, y):
        """Конвертация координат в координаты Canvas с учетом смещения начала координат."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        return (self.x0 + x * self.scale), (self.y0 - y * self.scale)

    def draw_pixel(self, x, y, for_line=True):
        """Рисование пикселя с учетом масштаба и смещения начала координат."""
        x, y = self.to_canvas_coords(x, y)
        self.canvas.create_rectangle(x, y, x + self.pixel_size * self.scale, y + self.pixel_size * self.scale, fill=self.line_color, outline=self.line_color, tags="line")

    def step_by_step(self, x1, y1, x2, y2):

        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        x_inc = dx / steps
        y_inc = dy / steps
        x, y = x1, y1
        for _ in range(steps):
            self.draw_pixel(round(x), round(y))
            x += x_inc
            y += y_inc

    def dda(self, x1, y1, x2, y2):
        self.step_by_step(x1, y1, x2, y2)

    def bresenham(self, x1, y1, x2, y2, draw=True):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            if draw:
                self.draw_pixel(x1, y1)
            if x1 == x2 and y1 == y2:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def bresenham_circle(self, xc, yc, radius, draw=True):
        x = 0
        y = radius
        d = 3 - 2 * radius
        while y >= x:
            for (dx, dy) in [(x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)]:
                if draw:
                    self.draw_pixel(xc + dx, yc + dy)
            x += 1
            if d > 0:
                y -= 1
                d += 4 * (x - y) + 10
            else:
                d += 4 * x + 6

    # Методы для перемещения начала координат
    def move_left(self):
        self.x0 += self.scale
        self.canvas.delete('line')
        self.draw_grid()

    def move_right(self):
        self.x0 -= self.scale
        self.canvas.delete('line')
        self.draw_grid()

    def move_up(self):
        self.y0 += self.scale
        self.canvas.delete('line')
        self.draw_grid()

    def move_down(self):
        self.y0 -= self.scale
        self.canvas.delete('line')
        self.draw_grid()
    
    def clear_all(self):
        self.canvas.delete('line')
        self.shapes.clear()

# Запуск приложения
root = tk.Tk()
app = RasterizationApp(root)
root.mainloop()
