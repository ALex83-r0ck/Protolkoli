from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import BooleanProperty
from kivymd.uix.card import MDCard
from kivymd.app import MDApp

class MyDraggableCard(MDCard):
    dragging = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._touch_offset_x = 0
        self._touch_offset_y = 0

    def on_touch_down(self, touch):
        # Check if touch is within the card
        #print("touch down", touch)
        if self.collide_point(*touch.pos) and touch.pos[1] > self.y + self.height * 0.9:
            self.dragging = True
            self._touch_offset_x = self.x - touch.x
            self._touch_offset_y = self.y - touch.y
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        # Move the card if dragging is enabled
        #print("touch move", touch)
        if self.dragging:
            self.x = touch.x + self._touch_offset_x
            self.y = touch.y + self._touch_offset_y
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        # Stop dragging when touch is released
        if self.dragging:
            self.dragging = False
            return True
        return super().on_touch_up(touch)