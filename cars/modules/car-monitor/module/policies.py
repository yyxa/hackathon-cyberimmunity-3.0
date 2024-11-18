# Политики безопасности
policies = (
    # dst car-network
    {"src": "car-verify-service", "dst": "car-network"},
    {"src": "car-verify-payment", "dst": "car-network"},
    {"src": "car-control", "dst": "car-network"},

    # dst car-verify-service
    {"src": "car-network", "dst": "car-verify-service"},
    {"src": "car-verify-payment", "dst": "car-verify-service"},

    # dst car-verify-payment
    {"src": "car-verify-service", "dst": "car-verify-payment"},

    # dst car-manager-service
    {"src": "car-verify-payment", "dst": "car-manager-service"},

    # dst car-control
    {"src": "car-network", "dst": "car-control"},
    {"src": "car-verify-service", "dst": "car-control"},
    {"src": "car-verify-geodata", "dst": "car-control"},
    {"src": "car-get-speed-from-geo", "dst": "car-control"},
    {"src": "car-verify-speed", "dst": "car-control"},
    {"src": "car-verify-driver", "dst": "car-control"},
    
    # dst car-verify-geodata
    {"src": "car-complex", "dst": "car-verify-geodata"},
    {"src": "car-network", "dst": "car-verify-geodata"},
    {"src": "car-adas", "dst": "car-verify-geodata"},
    {"src": "data", "dst": "car-verify-geodata"},

    # dst car-data
    {"src": "car-verify-geodata", "dst": "car-data"},
    {"src": "car-verify-speed", "dst": "car-data"},

    # dst car-get-speed-from-geo
    {"src": "car-gps", "dst": "car-get-speed-from-geo"},
    {"src": "car-glonass", "dst": "car-get-speed-from-geo"},
    
    # dst car-complex
    {"src": "car-gps", "dst": "car-complex"},
    {"src": "car-glonass", "dst": "car-complex"},

    # dst car-gps
    # 0    
    
    # dst car-glonass
    # 0   
    
    # dst car-monitoring
    {"src": "car-verify-payment", "dst": "car-monitoring"},
    {"src": "car-energy", "dst": "car-monitoring"},
    {"src": "car-skin-sensors", "dst": "car-monitoring"},
    
    # dst car-engine
    {"src": "car-monitoring", "dst": "car-engine"},
    {"src": "car-control", "dst": "car-engine"},
    {"src": "car-verify-driver", "dst": "car-engine"},
    
    # dst car-speed-lower
    {"src": "car-verify-speed", "dst": "car-speed-lower"},
    {"src": "car-control", "dst": "car-speed-lower"},
    {"src": "car-verify-driver", "dst": "car-speed-lower"},
    
    # dst car-verify-driver
    {"src": "car-camera", "dst": "car-verify-driver"},

    # dst car-camera
    # 0   
    
    # dst car-get-speed-from-camera
    {"src": "car-camera", "dst": "car-get-speed-from-camera"},
    
    # dst car-speed-sensors
    # 0  
    
    # dst car-adas
    # 0  
    
    # dst car-verify-speed
    {"src": "car-get-speed-from-camera", "dst": "car-verify-speed"},
    {"src": "car-speed-sensors", "dst": "car-verify-speed"},
    {"src": "car-adas", "dst": "car-verify-speed"},
    {"src": "car-get-speed-from-geo", "dst": "car-verify-speed"},
    {"src": "car-data", "dst": "car-verify-speed"}
    
    # dst car-energy
    # 0  
    
    # dst car-skin-sensors
    # 0  
)


def check_operation(id, details) -> bool:
    """ Проверка возможности совершения обращения. """
    src: str = details.get("source")
    dst: str = details.get("deliver_to")

    if not all((src, dst)):
        return False

    print(f"[info] checking policies for event {id}, {src}->{dst}")

    return {"src": src, "dst": dst} in policies
