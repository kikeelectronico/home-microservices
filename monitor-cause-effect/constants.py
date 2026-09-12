RULES = [
    {
        "device_id": "interruptor_prueba",
        "param": "on",
        "value": True,
        "reset_value": False,
        "effects": [
            {
                "device_id": "bombilla_prueba",
                "param": "on",
                "operator": "==",
                "value": True 
            }
        ]
    }
]