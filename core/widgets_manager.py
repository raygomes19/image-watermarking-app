import tkinter as tk
from tkinter import colorchooser
from tkinter.constants import HORIZONTAL

from config import config
from core.draggable_text import DraggableText
from core.fonts_manager import FontsManager


class WidgetsManager:
    def __init__(self, parent, canvas, update_func, **kwargs):
        self.parent = parent
        self.canvas = canvas
        self.update = update_func
        self.canvas_image = kwargs.get("canvas_image")
        self.font_color = kwargs.get("font_color")
        self.text = kwargs.get("text")
        self.draw = None

        # Initialize Fonts
        self.fonts_manager = FontsManager()
        self.fonts = self.fonts_manager.get_all_fonts()
        self.font_sizes = self.fonts_manager.font_sizes

        # Initialize UI
        self.init_ui(kwargs)

        # Bind events
        self.bind_window_events()
        self.bind_canvas_events()

        # Set default options
        self.set_default_options()

    def init_ui(self, kwargs):
        # UI Widgets
        label_kwargs = {"width": 15, "bg": config.BACKGROUND_COLOR_2}
        input_kwargs = {"width": 30, "highlightthickness": 0}

        self.text_label = tk.Label(self.parent, text="Text", **label_kwargs)
        self.text_input = tk.Entry(self.parent, textvariable=self.text, **input_kwargs)
        self.text_input.insert(0, config.DEFAULT_WATERMARK)

        self.size_label = tk.Label(self.parent, text="Font Size", **label_kwargs)
        self.size_input = self.create_listbox(self.font_sizes, input_kwargs)

        self.font_label = tk.Label(self.parent, text="Font Family", **label_kwargs)
        self.font_input = self.create_listbox(self.fonts, input_kwargs)

        self.font_style_label = tk.Label(self.parent, text="Font Style", **label_kwargs)
        self.font_style_input = tk.StringVar(self.parent, "normal")
        self.font_style_buttons = self.create_font_style_buttons()

        self.opacity_label = tk.Label(self.parent, text="Opacity", **label_kwargs)
        self.opacity_input = tk.Scale(
            self.parent, variable=kwargs.get("opacity"), from_=0, to=255, orient=HORIZONTAL, length=400,
            command=self.update, highlightthickness=0
        )

        self.font_color_label = tk.Label(self.parent, text="Font Color", **label_kwargs)
        self.color_picker_button = tk.Button(self.parent, text="Pick Color", command=self.choose_color,
                                             highlightthickness=0)
        self.font_color_display = tk.Frame(self.parent)
        self.font_color_box = tk.Label(self.font_color_display, bg=config.DEFAULT_FONT_COLOR_HEX, width=2)
        self.font_color_code = tk.Label(self.font_color_display, text=config.DEFAULT_FONT_COLOR_HEX)

        self.draggable_text = DraggableText(canvas=self.canvas, text=self.text.get(),
                                            font=self.get_font_style()["font"])

        self.render_watermark_inputs()

    def render_watermark_inputs(self):
        label_kwargs = {"column": 2, "sticky": "w", "padx": 10, "pady": 10}
        input_kwargs = {"column": 3, "sticky": "w", "padx": 10, "pady": 10}

        elements = [
            (self.text_label, self.text_input),
            (self.size_label, self.size_input),
            (self.font_label, self.font_input),
            (self.font_style_label, self.font_style_buttons["normal"]),
            (None, self.font_style_buttons["bold"]),
            (None, self.font_style_buttons["italic"]),
            (self.opacity_label, self.opacity_input),
            (self.font_color_label, self.color_picker_button),
            (None, self.font_color_display)
        ]

        for i, (label, input_) in enumerate(elements, start=1):
            if label:
                label.grid(row=i, **label_kwargs)
            input_.grid(row=i, **input_kwargs)

        self.font_color_box.grid(row=0, column=0)
        self.font_color_code.grid(row=0, column=1, padx=10)

    def bind_canvas_events(self):
        self.canvas.tag_bind(self.canvas_image, "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind(self.canvas_image, "<B1-Motion>", self.on_drag_motion)
        self.canvas.tag_bind(self.canvas_image, "<ButtonRelease-1>", self.on_drag_end)

    def bind_window_events(self):
        event_bindings = {
            '<KeyRelease>': [self.text_input, self.size_input, self.font_input],
            '<ButtonRelease-1>': [self.size_input, self.font_input],
        }
        for e, widgets in event_bindings.items():
            for w in widgets:
                w.bind(e, self.update)

        self.text.trace_add("write", self.on_text_change)  # Listen for changes

    def create_font_style_buttons(self):
        # TODO: Feature - Combine style of fonts - normal, bold, italic

        button_kwargs = {
            "variable": self.font_style_input, "indicatoron": False, "width": 10, "command": self.update,
            "highlightthickness": 0, "selectcolor": "#616161"
        }

        return {style: tk.Radiobutton(self.parent, text=style.capitalize(), value=style, **button_kwargs)
                for style in ["normal", "bold", "italic"]}

    def create_listbox(self, items, kwargs):
        listbox = tk.Listbox(self.parent, exportselection=0, height=3, **kwargs)
        for i, item in enumerate(items):
            listbox.insert(i, item)
        return listbox

    def get_font_style(self):
        size_index = self.size_input.curselection()
        font_index = self.font_input.curselection()
        font_size = self.font_sizes[size_index[0] if size_index else 0]
        font_name = self.fonts[font_index[0] if font_index else 0]
        font_style = self.font_style_input.get()

        return {
            "font": self.fonts_manager.get_font(font_name, font_size, style=font_style),
            "size": font_size,
            "style": font_style,
            "name": font_name
        }

    def update_image_draw(self, draw):
        self.draw = draw

    def choose_color(self):
        font_color = colorchooser.askcolor(title="Font Color", initialcolor=self.font_color_code.cget("text"))
        if font_color != (None, None):
            self.font_color.set(str(font_color[0]))
            self.update_selected_color(font_color[1])
            self.update()

    def update_selected_color(self, color):
        self.font_color_code.config(text=str(color))
        self.font_color_box.config(bg=str(color))

    def on_text_change(self, name, index, mode):
        self.draggable_text.set_text(self.text.get())

    def on_drag_start(self, event):
        self.draggable_text.font = self.get_font_style()["font"]
        self.draggable_text.on_drag_start(event, self.draw)

    def on_drag_motion(self, event):
        if self.draggable_text.dragging:
            self.draggable_text.on_drag_motion(event, self.draw)
            self.update()

    def on_drag_end(self, event):
        self.draggable_text.on_drag_end(event)

    def set_listbox_selection(self, listbox, index):
        listbox.selection_clear(0, tk.END)
        listbox.select_set(index)
        listbox.activate(index)
        listbox.see(index)
        listbox.event_generate("<<ListboxSelect>>")

    def set_default_options(self):
        self.set_listbox_selection(self.size_input, self.font_sizes.index(config.DEFAULT_FONT_SIZE))
        self.set_listbox_selection(self.font_input, self.fonts.index(config.DEFAULT_FONT))
        self.font_style_input.set(config.DEFAULT_FONT_STYLE)
        self.opacity_input.set(config.DEFAULT_OPACITY)
        self.font_color.set(config.DEFAULT_FONT_COLOR_RGB)
        self.update_selected_color(config.DEFAULT_FONT_COLOR_HEX)

        self.draggable_text.set_coordinates(config.INITIAL_POSITION)
        self.draggable_text.set_text(config.DEFAULT_WATERMARK)
        self.text.set(config.DEFAULT_WATERMARK)
