from datetime_manager import check_events, save_event
import time
save_event("test", int(time.time()), 1)
print(check_events())
