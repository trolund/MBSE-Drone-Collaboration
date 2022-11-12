class Settings:

    def __init__(self, config):

        # simulation config
        a = config["setup"]["fixed_truck_pos"].split(",")
        self.fixed_truck_pos = (int(a[0]), int(a[1]))
        self.world_size = int(config["setup"]["world_size"])
        self.ground_size = int(config["setup"]["ground_size"])
        self.road_size = int(config["setup"]["road_size"])
        self.customer_density = float(config["setup"]["customer_density"])
        self.optimal_truck_pos = False if config["setup"]["optimal_truck_pos"] == "0" else True
        self.number_of_tasks = int(config["setup"]["number_of_tasks"])
        self.number_of_drones = int(config["setup"]["number_of_drones"])
        self.truck_pos = None
        self.seed = None

        # screen
        self.scale = float(config["graphics"]["scale"])
        self.is_fullscreen = False if config["graphics"]["fullscreen"] == "0" else True
        self.width = float(config["graphics"]["window_w"])
        self.height = float(config["graphics"]["window_h"])




