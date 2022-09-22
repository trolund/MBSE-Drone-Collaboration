import pygame
import pygame_gui
from pygame.surface import Surface


class UI:

    def __init__(self, screen: Surface):
        self.ui_width = 400
        self.margin = 30

        self.ui_width = screen.get_width() - self.ui_width
        self.ui_x = self.ui_width

        self.screen = screen
        self.manager = pygame_gui.UIManager((screen.get_width(), screen.get_height()))

        self.use_battery = False

        self.create_ui_elements()

    def create_ui_elements(self):

        self.use_battery_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.ui_x + self.margin, 500, 100, 30),
            text="True" if self.use_battery else "False",
            manager=self.manager
        )

        self.button1 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.ui_x + self.margin, 400, 100, 30),
            text='Click me 1',
            manager=self.manager
        )

        self.button2 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.ui_x + self.margin, 200, 100, 30),
            text='Click me 2',
            manager=self.manager
        )

        self.label1 = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.ui_x + self.margin, 100, 200, 100),
            text="Value",
            manager=self.manager
        )

    def handle_events(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.button1:
                    self.label1.set_text("click 1")
                    print("click 1")
                if event.ui_element == self.button2:
                    self.label1.set_text("click 2")
                    print("click 2")
                if event.ui_element == self.use_battery_btn:
                    self.use_battery = not self.use_battery
                    self.use_battery_btn.set_text(str(self.use_battery))

        self.manager.process_events(event)

    def draw(self, time_delta):
        pygame.draw.rect(self.screen, (220, 220, 222), pygame.Rect(self.ui_x, 0, self.ui_width, self.screen.get_height()))
        self.manager.update(time_delta)
        self.manager.draw_ui(self.screen)

    def get_manager(self):
        return self.manager
