
MAP_SIZE = 200
LAND_LOCATIONS = [(50, 80), (50, 100)]
TOTAL_TIMESTEPS = 300

POPULATION = {
    "penguin": 1,
    "seal": 0,
    "fish": 200
}

INITIAL_LOCATIONS = {
    "fish": (150, 50), 
    "penguin": (70, 70), 
    "seal": (10, 10)}

PARAMS = {
    "fish": {
        "energy": None,
        "speed": {"walk": 2.0, "run": 2.0},
        "alert": {"escape": 15.0, "home": 10.0}
    },
    "penguin": {
        "energy": 30,
        "speed": {"walk": 1.0, "run": 3.0},
        "alert": {"hunt": 50.0, "escape": 10.0}
    },
    "seal": {
        "energy": 30,
        "speed": {"walk": 2.0, "run": 5.0},
        "alert": {"hunt": 100.0}
    }
}

