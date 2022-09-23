import os

import pygame
import pygame_gui
from dependency_injector.wiring import Provide
from pygame.surface import Surface
from pygame_gui.core import ObjectID

from Logging.eventlogger import EventLogger
from Models.colors import GREY
from containers import Container


class UI:

    def __init__(self, screen: Surface, logger: EventLogger = Provide[Container.event_logger]):
        self.logger = logger
        self.ui_width = 400
        self.margin = 30

        self.ui_width = screen.get_width() - self.ui_width
        self.ui_x = self.ui_width

        self.screen = screen
        self.manager = pygame_gui.UIManager((screen.get_width(), screen.get_height()), os.path.join("GUI", 'theme.json'))

        self.use_battery = False
        self.log = []

        self.create_ui_elements()

    def create_ui_elements(self):

        self.use_battery_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.ui_x + self.margin, 500, 100, 30),
            text="True" if self.use_battery else "False",
            manager=self.manager
        )

        self.button1 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.ui_x + self.margin, 400, 100, 30),
            text='Pause',
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

        self.delta_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.screen.get_width() - 150, self.screen.get_height() - 80, 200, 100),
            text="Delta: 0.0",
            manager=self.manager,
            object_id=ObjectID(class_id='#debug_text')
        )

        self.FPS_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.screen.get_width() - 150, self.screen.get_height() - 60, 200, 100),
            text="FPS: 0.0",
            manager=self.manager,
            object_id=ObjectID(class_id='#debug_text')
        )

        self.list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(self.ui_x, self.screen.get_height() - 200, 400, 150),
            manager=self.manager, item_list=[]
        )

    def handle_events(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.button1:
                    # self.pause_game(event)
                    print("pause")
                if event.ui_element == self.button2:
                    self.label1.set_text("click 2")
                    print("click 2")
                if event.ui_element == self.use_battery_btn:
                    self.use_battery = not self.use_battery
                    self.use_battery_btn.set_text(str(self.use_battery))

        self.manager.process_events(event)

    def update(self, time_delta: float, fps: float):
        pygame.draw.rect(self.screen, GREY, pygame.Rect(self.ui_x, 0, self.ui_width, self.screen.get_height()))
        self.delta_label.set_text("Delta: " + str(time_delta))
        self.FPS_label.set_text("FPS: " + str(fps))
        self.list.set_item_list(self.logger.get_log())
        self.manager.update(time_delta)
        self.manager.draw_ui(self.screen)

    def get_manager(self):
        return self.manager