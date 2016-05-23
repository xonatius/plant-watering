plants_pumps_config = {
        "Succulent" : {
            "forward_pin" : 17,
            "ml_per_second" : 1.0,
            "inverse" : True
            },
        "Pineapple Right" : {
            "forward_pin" : 27,
            "ml_per_second" : 1.0,
            "inverse" : True
            },
        "Pineapple Left" : {
            "forward_pin" : 22,
            "ml_per_second" : 1.0,
            "inverse" : True
            },
        "Basil" : {
            "forward_pin" : 23,
            "ml_per_second" : 1.0,
            "inverse" : True
            },
        "Empty" : {
            "forward_pin" : 24,
            "ml_per_second" : 1.0,
            "inverse" : True
            },
        "Orchid" : {
            "forward_pin" : 5,
            "backward_pin" : 6,
            "ml_per_second" : 0.5,
            "inverse" : False
            }
        }

plants = sorted(plants_pumps_config.keys())
