from config import config


class DraggableText:
    def __init__(self, canvas, text, font):
        self.canvas = canvas
        self.font = font
        self.text = text

        # Initial text position
        self.text_x, self.text_y = config.INITIAL_POSITION

        # Track dragging state
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def set_coordinates(self, coordinates):
        x, y = coordinates
        self.text_x = x
        self.text_y = y

    def get_current_coordinates(self):
        return self.text_x, self.text_y

    def set_text(self, text):
        self.text = text

    def get_textbox_dim(self, draw):
        bbox = draw.textbbox((self.text_x, self.text_y), self.text, font=self.font, anchor=config.TEXT_ANCHOR)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        return text_width, text_height

    def on_drag_start(self, event, draw):
        text_width, text_height = self.get_textbox_dim(draw)

        # Check if cursor is within bounds of textarea
        if self.text_x <= event.x <= self.text_x + text_width and self.text_y <= event.y <= self.text_y + text_height:
            self.dragging = True
            self.offset_x = event.x - self.text_x
            self.offset_y = event.y - self.text_y

    def on_drag_motion(self, event, draw):
        if self.dragging:
            text_width, text_height = self.get_textbox_dim(draw)

            # Update text position within boundaries
            self.text_x = max(0, min(event.x - self.offset_x, self.canvas.winfo_reqwidth() - text_width))
            self.text_y = max(0, min(event.y - self.offset_y, self.canvas.winfo_reqheight() - text_height))

    def on_drag_end(self, event):
        self.dragging = False
