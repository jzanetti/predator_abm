
MAP_SIZE = 200
LAND_LOCATIONS = [
    [(50, 80), (50, 100)],
    [(150, 175), (25, 50)]
]

CLIMATE_VARS = {
    "ice_stability_index": 0.03,  # A value between 0 and 1 that determines how quickly the ice melts. Higher means faster melt.
}

TOTAL_TIMESTEPS = 300

POPULATION = {
    "penguin": 15,
    "seal": 0,
    "fish": 200
}

INITIAL_LOCATIONS = {
    "fish": (150, 50), 
    "penguin": (70, 70), 
    "seal": (0, 0)}

PARAMS = {
    "fish": {
        "energy": None,
        "speed": {"walk": 2.0, "run": 2.0},
        "vision": {"escape": 15.0, "home": 10.0},
        "hunt_success_rate": None,
    },
    "penguin": {
        "energy": 30,
        "speed": {"walk": 1.0, "run": 5.0},
        "vision": {"hunt": 50.0, "escape": 10.0},
        "hunt_success_rate": 0.5,
        "max_travel_distance": 350.0
    },
    "seal": {
        "energy": 30,
        "speed": {"walk": 1.0, "run": 8.0},
        "vision": {"hunt": 100.0},
        "hunt_success_rate": 0.15
    }
}

