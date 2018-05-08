from threading import Lock

changed_teds = []
scripts_list = []
actuator_update = False
sensor_data_lock = Lock()
actuator_data_lock = Lock()
changed_teds_lock = Lock()
message_read = False
message_lock = Lock()
