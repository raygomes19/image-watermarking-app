import os.path
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar

from PIL import Image, ImageTk, ImageDraw

from config import config
from core.widgets_manager import WidgetsManager
from utils import format_image_size


class WatermarkApplication:
    def __init__(self):
        self.init_variables()

        self.root = self.setup_window()
        self.config_menu()
        self.setup_widgets()

        # Test code
        self.root.after(1000, self.upload_file, True)

        # Run window
        self.root.mainloop()

    def init_variables(self):
        self.scale_factor = 1
        self.watermarked_image = None
        self.tk_image = None
        self.preview_image = None
        self.original_image = None

    def setup_window(self):
        root = tk.Tk()
        root.title("Image Watermarking App")
        root.config(padx=config.WINDOW_PAD_X, pady=config.WINDOW_PAD_Y, bg=config.BACKGROUND_COLOR)
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
        return root

    def config_menu(self):
        menubar = tk.Menu(self.root)
        menubar.add_command(label="Select File", command=self.frame_select_file)
        menubar.add_command(label="Save File", command=self.save)
        self.root.config(menu=menubar)

    def setup_widgets(self):
        # TODO: Fix warning --> Instance attribute defined outside __init__

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.setup_frames()

        # Upload button
        upload_button = tk.Button(self.select_file_frame, text="Select File", command=self.upload_file)
        upload_button.pack(expand=True)  # Centers the button

        # Canvas
        self.setup_canvas()

        # Widgets
        self.setup_widgets_panel()

    def setup_frames(self):
        self.select_file_frame = tk.Frame(self.root)
        self.watermark_frame = tk.Frame(self.root, bg=config.BACKGROUND_COLOR)
        self.watermark_frame.grid_columnconfigure(0, weight=2)

    def setup_canvas(self):
        self.canvas_frame = tk.Frame(self.watermark_frame, width=config.CANVAS_WIDTH, height=config.CANVAS_HEIGHT,
                                     bg=config.BACKGROUND_COLOR_2)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.canvas_frame.grid_columnconfigure(0, weight=1)  # Allows stretching
        self.canvas_frame.grid_rowconfigure(0, weight=1)  # Ensures centering
        self.canvas_frame.grid_rowconfigure(1, weight=0)  # Prevents image heading from shrinking

        self.canvas = tk.Canvas(self.canvas_frame, width=config.CANVAS_WIDTH, height=config.CANVAS_HEIGHT,
                                highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW)

        self.image_heading = tk.Label(self.canvas_frame, text="Image Name and size", bg=config.BACKGROUND_COLOR_2)
        self.image_heading.grid(row=1, column=0, sticky="sew", pady=10)

    def setup_widgets_panel(self):
        self.widgets_frame = tk.Frame(self.watermark_frame, bg=config.BACKGROUND_COLOR_2)
        self.widgets_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10, ipadx=10)

        widget_heading = tk.Label(self.widgets_frame, text="Options", bg=config.BACKGROUND_COLOR_2)
        widget_heading.grid(row=0, column=1, columnspan=4, sticky="ew", pady=10)

        # Widgets variables
        self.text = StringVar()
        self.opacity = tk.IntVar(value=255)
        self.font_color = StringVar()
        self.widgets = WidgetsManager(self.widgets_frame, self.canvas, self.update_watermark,
                                      canvas_image=self.canvas_image,
                                      text=self.text, opacity=self.opacity, font_color=self.font_color)

    def show_upload_frame(self):
        self.select_file_frame.grid(row=0, column=0, sticky="nsew")

    def show_watermark_frame(self):
        self.watermark_frame.grid(row=0, column=0, sticky="nsew")

    def frame_select_file(self):
        self.original_image = None
        self.show_upload_frame()
        self.watermark_frame.grid_forget()

    def upload_file(self, test=False):
        test_file_path = os.path.join(config.IMAGE_DIR, "1440x900.png")
        file_path = test_file_path if test else filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])

        if not file_path:
            messagebox.showinfo("Error", message=f"Cannot open file {file_path}")
            self.frame_select_file()
            return

        print(f"Selected File: {file_path}")
        try:
            self.original_image = Image.open(file_path)
        except IOError:
            # TODO: Style the messagebox to display errors in a better way
            messagebox.showinfo("Error", message=f"Cannot open file {file_path}")
            self.frame_select_file()
            return

        self.preview_image = self.original_image.copy()
        self.preview_image.thumbnail(config.THUMBNAIL_SIZE)
        self.tk_image = ImageTk.PhotoImage(self.preview_image)
        self.canvas.config(width=self.preview_image.width, height=self.preview_image.height)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_image)

        self.scale_factor = self.original_image.width / self.preview_image.width
        self.image_heading.config(
            text=f"Selected File: {file_path}\nOriginal Image Size: {format_image_size(self.original_image.size)} "
                 f"| Resized Image Size: {format_image_size(self.preview_image.size)}")

        self.select_file_frame.grid_forget()
        self.widgets.set_default_options()
        self.show_watermark_frame()
        self.update_watermark()

    def save(self):
        if not self.original_image:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"),
                                                            ("All Files", "*.*")])
        if file_path:
            watermark = Image.new("RGBA", self.original_image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            self.widgets.update_image_draw(draw)

            options = self.get_selected_options()
            scaled_x, scaled_y = int(options["x"] * self.scale_factor), int(
                options["y"] * self.scale_factor)

            scaled_font_size = int(options["font_size"] * self.scale_factor)
            font = self.widgets.fonts_manager.get_font(options["font_name"], scaled_font_size, options["font_style"])

            draw.text((scaled_x, scaled_y), options["text"], font=font, fill=options["color"],
                      anchor=config.TEXT_ANCHOR)

            watermarked = Image.alpha_composite(self.original_image.convert("RGBA"), watermark)
            watermarked.convert("RGB").save(file_path, "PNG")

            print(f"Saved image size: {watermarked.size}")
            print(f"Image saved as {file_path}")

    def update_watermark(self, event=None):
        options = self.get_selected_options()
        x, y, text, color, font = options["x"], options["y"], options["text"], options["color"], options["font"]

        watermark_overlay = Image.new("RGBA", self.preview_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_overlay)
        self.widgets.update_image_draw(draw)

        draw.text((x, y), text, font=font, fill=color, anchor=config.TEXT_ANCHOR)

        watermarked_image = Image.alpha_composite(self.preview_image.convert("RGBA"), watermark_overlay)
        self.tk_image = ImageTk.PhotoImage(watermarked_image)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_image)
        self.show_watermark_frame()

    def get_selected_options(self):
        x, y = self.widgets.draggable_text.get_current_coordinates()
        font_style = self.widgets.get_font_style()
        opacity = self.opacity.get()
        rgb = tuple(map(int, self.font_color.get().strip("()").split(
            ","))) if self.font_color.get() else config.DEFAULT_FONT_COLOR_RGB
        color_with_opacity = (rgb[0], rgb[1], rgb[2], opacity)

        return {
            "x": x,
            "y": y,
            "text": self.text.get() or config.DEFAULT_WATERMARK,
            "color": color_with_opacity,
            "font": font_style["font"],
            "font_name": font_style["name"],
            "font_size": font_style["size"],
            "font_style": font_style["style"],
        }
