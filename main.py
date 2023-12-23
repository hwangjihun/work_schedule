import json
from misc_util import find_previous_schedule, find_available_workers, create_current_kyohuan, set_current_schedule_date
from datetime import datetime

# Load Previous Day's Work Schedule
prev_schedule = open(f'./archive/json/{find_previous_schedule()}.json')
prev_schedule = json.load(prev_schedule)

# Load All Workers
workers_db = open('workers.json')
workers_db = json.load(workers_db)

available_workers = find_available_workers()
current_date = set_current_schedule_date()

updated_schedule = {}

# Weekday
if (datetime.strptime(current_date, "%Y-%m-%d").weekday() < 5):
    updated_schedule = create_current_kyohuan(prev_schedule, available_workers)
    print(updated_schedule)