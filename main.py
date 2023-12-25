import json
from misc_util import (
    find_previous_schedule, find_available_workers,
    allocate_current_kyohuan, set_current_schedule_date,
    allocate_two_times, fill_remaining
) 
from datetime import datetime

def sort_schedule(x): 
    return int(x["workTime"])

# Load Previous Day's Work Schedule
prev_schedule = open(f'./archive/json/{find_previous_schedule()}.json')
prev_schedule = json.load(prev_schedule)

# Load All Workers
workers_db = open('workers.json')
workers_db = json.load(workers_db)

available_workers = find_available_workers()
current_date = set_current_schedule_date()

current_schedule = {"members": []}

# Weekday
if (datetime.strptime(current_date, "%Y-%m-%d").weekday() < 5):
    # Allocate Current Kyohuan
    next_kyohuan, current_schedule, previous_kyohuan = allocate_current_kyohuan(prev_schedule, available_workers)
 
    # Allocate 2 탕 근무자 (if there is a need)
    current_schedule = allocate_two_times(current_schedule, available_workers, next_kyohuan, False)
    
    # Filling in the remaining workers
    current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, previous_kyohuan)


# Saturday is special because we have to exclude friday's kyohuan
# 휴무 IS INCLUDED HERE IF it is before a weekday

elif (datetime.strptime(current_date, "%Y-%m-%d").weekday() == 5):
    previous_kyohuan = list(set([i["name"] for i in prev_schedule["members"] if i["workTime"] < 5]))
     # Allocate 2 탕 근무자 (if there is a need)
    current_schedule = allocate_two_times(current_schedule, available_workers, [], True)
    # Filling in the remaining workers
    current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, previous_kyohuan)

else:
    # Allocate 2 탕 근무자 (if there is a need)
    current_schedule = allocate_two_times(current_schedule, available_workers, [], True)
    # Filling in the remaining workers
    current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, [])

sorted_schedule = sorted(current_schedule["members"], key=sort_schedule)

formatted_sorted_schedule = {
    "members": sorted_schedule
}

json_object = json.dumps(formatted_sorted_schedule, indent=4, ensure_ascii=False)


with open(f"./archive/json/{current_date}.json", "w") as outfile:
    outfile.write(json_object)