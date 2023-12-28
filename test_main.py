import json
from misc_util import (
    find_previous_schedule, 
    test_find_available_workers, find_available_workers,
    allocate_current_kyohuan,
    allocate_two_times, fill_remaining
) 
from datetime import datetime, timedelta
def sort_schedule(x): 
    return int(x["workTime"])

# Load the date to plan
calendar = open("./archive/timetable/january2024.json")
calendar = json.load(calendar)

unplanned_dates = {date: info for date, info in calendar.items() if info['isPlanned'] == False}
unplanned_dates = list(unplanned_dates.keys())

# The date to plan
current_date = unplanned_dates[0]
previous_date = datetime.strptime(unplanned_dates[0], '%Y-%m-%d') - timedelta(days=1)
previous_date = datetime.strftime(previous_date, '%Y-%m-%d')

# Load Previous Day's Work Schedule
prev_schedule = open(f'./archive/json/{previous_date}.json')
prev_schedule = json.load(prev_schedule)

available_workers = test_find_available_workers(current_date, calendar)


current_schedule = {"members": []}

if (calendar[current_date]["isHoliday"]):
    if (calendar[previous_date]["isHoliday"]):
        # Allocate 2 탕 근무자 (if there is a need)
        current_schedule = allocate_two_times(current_schedule, available_workers, [], True, current_date)
        # Filling in the remaining workers
        current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, [])
    elif (calendar[previous_date]["isHoliday"] == False):
        previous_kyohuan = list(set([i["name"] for i in prev_schedule["members"] if i["workTime"] < 5]))
        # Allocate 2 탕 근무자 (if there is a need)
        current_schedule = allocate_two_times(current_schedule, available_workers, [], True, current_date)
        # Filling in the remaining workers
        current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, previous_kyohuan)
elif (calendar[current_date]["isHoliday"] == False):
    # Filter for Planned Dates (latest previous work day)
    planned_dates = {date: info for date, info in calendar.items() if info['isPlanned'] == True and info['isHoliday'] == False and info["isTraining"] == False}
    latest_previous_work_day = list(planned_dates.keys())[-1]
    prev_schedule = open(f'./archive/json/{latest_previous_work_day}.json')
    prev_schedule = json.load(prev_schedule)

    # Allocate Current Kyohuan
    next_kyohuan, current_schedule, previous_kyohuan = allocate_current_kyohuan(prev_schedule, available_workers)
    
    # Allocate 2 탕 근무자 (if there is a need)
    current_schedule = allocate_two_times(current_schedule, available_workers, next_kyohuan, False, current_date)
        
    # Filling in the remaining workers
    current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, previous_kyohuan)
   

sorted_schedule = sorted(current_schedule["members"], key=sort_schedule)

formatted_sorted_schedule = {
    "members": sorted_schedule
}

json_object = json.dumps(formatted_sorted_schedule, indent=4, ensure_ascii=False)


with open(f"./archive/json/{current_date}.json", "w") as outfile:
    outfile.write(json_object)

calendar[current_date]['isPlanned'] = True

print(calendar)
with open(f"./archive/timetable/january2024.json", 'w') as json_file:
    json.dump(calendar, json_file, indent=4)
