import datetime
import pygame
from dependency_injector.wiring import Provide

from GUI.UI import UI
from Logging.eventlogger import EventLogger, LogFile
from Models.settings import Settings
from Models.colors import WHITE, GREY, BLACK
from Models.drone import Drone
from Models.env import Env
from Models.setup import FPS
from Models.truck import Truck
from Services.Task_creater import create_random_tasks
from Services.drone_controller import DroneController
from Services.path_finder import PatchFinder
from Services.task_manager import TaskManager
from Utils.CompelxityCalulator import calc_complexity
from Utils.Timer import Timer
from Utils.layout_utils import draw_layout, grid_to_pos, get_world_size, create_layout_env, translate_moves
from containers import Container

pygame.init()
pygame.font.init()
pygame.mixer.init()

font = pygame.font.Font(None, 40)

name = "DRONE SIMULATION - MBSE - GROUP 2 (2022)"


class Simulation(object):

    def __init__(self, logger: EventLogger = Provide[Container.event_logger],
                 config=Provide[Container.config],
                 env: Env = Provide[Container.env]):

        pygame.display.set_caption(name)

        logger.log("Starting Simulation - " + name, show_in_ui=False)


        self.settings = Settings(config)
        logger.log("Config loaded ", show_in_ui=False)
        self.logger = logger
        self.drone_controller = None
        self.task_manager = None

        self.env = env
        self.config = config
        self.is_paused = False
        self.is_running = True

        self.screen = None
        self.drones_ref = None

        self.OffsetX = 0
        self.OffsetY = 0

        # create the window from config
        self.create_window()

        self.Main()

    def create_drones(self, env: Env, step_size, number_of_drones: int):

        self.drones_ref = []

        for d in range(0, number_of_drones):
            drone = Drone(self.settings.scale, "drone_" + str(d))
            # start at x, y
            drone.rect.x = env.home[0]
            drone.rect.y = env.home[1]
            env.sprites.add(drone)
            self.drones_ref.append(drone)

        self.drone_controller = DroneController(self.task_manager, self.drones_ref, step_size)

    def create_tasks(self, env: Env, possible_addresses, number_of_tasks):

        tasks = create_random_tasks(possible_addresses, number_of_tasks)

        for idx, t in enumerate(tasks):
            # start at truck
            # t.rect.x = env.home[0]  # + (5 * idx)
            # t.rect.y = env.home[1]

            env.task_ref.append(t)
            env.sprites.add(t)

        self.task_manager = TaskManager()

    def create_truck(self, layout, step_size, env: Env, pos):
        route = None

        if self.settings.moving_truck:
            planner = PatchFinder()
            route = planner.find_path(layout, (0, 0), (len(layout) - 1, len(layout) - 1))
            route = translate_moves(route, step_size)

        self.logger.log("Starting Position of truck - " + str(pos), show_in_ui=False)
        truck = Truck(pos, path=route, size=step_size, packages=env.task_ref)
        env.home = truck.get_home()
        env.sprites.add(truck)

    def draw_layers(self, layout, x_len: int, y_len: int, step_size: int, env):
        # draw the basic layout
        draw_layout(self.screen, layout, x_len, y_len, step_size, self.settings.scale, self.OffsetX, self.OffsetY)

        # draw all sprites on top of layout
        for t in env.sprites:
            # scale images
            t.image = pygame.transform.scale(t.images[0],
                                             (t.width * self.settings.scale, t.height * self.settings.scale))
            self.screen.blit(t.image, [(t.rect.x * self.settings.scale + self.OffsetX),
                                       (t.rect.y * self.settings.scale + self.OffsetY)])

    def set_scale(self, val):
        temp = self.settings.scale + val
        if temp < 1:
            self.settings.scale = 1
            # self.adjust_zoom_offset(val)
        else:
            if not temp > 10:
                self.settings.scale = temp
                # self.adjust_zoom_offset(val)

    def toggle_paused(self, btn):
        self.is_paused = not self.is_paused
        btn.set_text("▶ Resume" if self.is_paused else "Pause")

    def adjust_zoom_offset(self, change):
        locationX = (self.settings.world_size - self.screen.get_width()) / self.settings.scale
        locationY = (self.settings.world_size - self.screen.get_height()) / self.settings.scale

        if change < 0:
            self.OffsetX += locationX
            self.OffsetY += locationY
        else:
            self.OffsetX -= locationX
            self.OffsetY -= locationY

    def create_window(self):
        if self.settings.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.settings.width, self.settings.height))

    def keyboard_input(self):
        offset_factor = 5
        zoom_factor = 0.2

        keys = pygame.key.get_pressed()  # checking pressed keys

        # move camera
        if keys[pygame.K_LEFT]:
            self.OffsetX += offset_factor
        if keys[pygame.K_RIGHT]:
            self.OffsetX -= offset_factor
        if keys[pygame.K_UP]:
            self.OffsetY += offset_factor
        if keys[pygame.K_DOWN]:
            self.OffsetY -= offset_factor

        # zoom
        if keys[pygame.K_u]:
            self.set_scale(zoom_factor)
        if keys[pygame.K_d]:
            self.set_scale(-zoom_factor)

    def draw_paused(self):
        text = font.render('Paused', True, GREY, BLACK)

        # create a rectangular object for the
        # text surface object
        textRect = text.get_rect()

        # set the center of the rectangular object.
        textRect.center = ((self.screen.get_width() - 400) // 2, self.screen.get_height() // 2)

        self.screen.blit(text, textRect)



    def _on_tick(self, delta):
        self.keyboard_input()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gl.is_running = False
            self.ui.handle_events(event)
        
        self.ui.on_tick(delta)
        for sprite in self.env.sprites:
            sprite.on_tick(delta)
        # only 'count' time if nor paused
        self.timer.add_delta_time(delta)
        self.drone_controller.assign_tasks()


    def _on_frame(self, delta_frame):
        if self.is_paused:
            self.draw_paused()
        # clear background
        self.screen.fill(WHITE)
        # draw object layers
        self.draw_layers(self.layout, self.x_len, self.y_len, self.step_size, self.env)

        # update and draw UI
        self.ui.on_frame(self.settings.scale, self.timer)

        pygame.display.flip()

        # update screen with new drawings
        pygame.display.update()

    def set_simulation_speed(self, scale):
        self.gl.scale_simulation(scale)


    def Main(self):
        # instance of UI
        self.ui = UI(self.set_scale, self.set_simulation_speed, self.toggle_paused, self.settings, self.screen)

        # setup layout
        (self.layout, delivery_sports, number_of_grounds, number_of_customers), truck_pos = create_layout_env(
            self.settings.world_size,
            self.settings.ground_size,
            road_size=self.settings.road_size,
            customer_density=self.settings.customer_density,
            optimal_truck_pos=self.settings.optimal_truck_pos)
        (self.step_size, self.x_len, self.y_len, self.settings.scale) = get_world_size(self.screen, self.layout)

        # create all objects in the environment
        self.create_tasks(self.env, delivery_sports, self.settings.number_of_tasks)
        self.create_truck(self.layout, self.step_size, self.env, grid_to_pos(0, 0, self.step_size))
        self.create_drones(self.env, self.step_size, self.settings.number_of_drones)

        self.logger.log(f"ENV Complexity: {calc_complexity(number_of_customers, self.settings.world_size, delivery_sports, truck_pos, self.settings.number_of_drones, self.settings.number_of_tasks)}")

        # Simulation/game loop
        self.timer = Timer()

        from game_loop import GameLoop

        self.gl = GameLoop(
            self._on_tick,
            self._on_frame, 
            lambda ticks, frames : self.logger.log(f'TPS: {ticks} | FPS: {frames}')
        )
        self.gl.start()

        pygame.quit()


if __name__ == "__main__":
    # setup dependency injection
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    Simulation()
