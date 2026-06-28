
MAP_SIZE = 200
LAND_LOCATIONS = [
    [(50, 80), (50, 100)],
    [(150, 175), (25, 50)]
]

CLIMATE_VARS = {
    # Reduced drastically. At 1 timestep = 1 hour, a 3% melt rate would destroy 
    # the land in days. 0.1% per hour allows for gradual melting over 3 months.
    "ice_stability_index": 0.001,  
}

# 3 months ≈ 90 days. 
# 90 days * 24 hours/day = 2160 hours. 
# 2160 hours / 3 hours per step = 720 timesteps.
TOTAL_TIMESTEPS = 300

POPULATION = {
    "penguin": 50,
    "seal": 0,      
    "fish": 800     
}

INITIAL_LOCATIONS = {
    "fish": (150, 50), 
    "penguin": (70, 70), 
    "seal": (0, 0)}

PARAMS = {
    "fish": {
            "energy": None,
            "speed": {"walk": 2.0, "run": 4.0},     # 2 km/h cruise, 4 km/h burst
            "vision": {"escape": 2.0, "home": 2.0}, # 6 km vision (2 grids * 3km)
            "hunt_success_rate": None,
    },
    "penguin": {
            # A 5-day foraging trip = 120 hours.
            # 120 hours / 3 hours per step = 40 energy steps.
            "energy": {"max": 40, "burn_rate": {"water": {"walk": 1.0, "run": 3.0}, "land": 0.2}},  
            "speed": {"walk": 7.0, "run": 15.0},    # 7 km/h cruise, 15 km/h sprint
            "vision": {"hunt": 4.0, "escape": 2.0}, # 12 km hunt vision, 6 km escape vision
            "hunt_success_rate": 0.4,
            # Max real-world travel distance ~1000 km.
            # 1000 km / 3 km per grid = 333 grid units.
            # "max_travel_distance": 333.0 
        },
    "seal": {
            "energy": 40,                           # 120 hours equivalent
            "speed": {"walk": 10.0, "run": 30.0},   # 10 km/h cruise, 30 km/h sprint
            "vision": {"hunt": 5.0},                # 15 km vision (5 grids * 3km)
            "hunt_success_rate": 0.20               
    }
}

