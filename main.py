import json
from alpha_util import (
    find_available_workers,
    allocate_current_kyohuan,
    allocate_two_times,
    fill_remaining
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

available_workers, exempted_workers = find_available_workers(current_date, calendar)
current_schedule = {"members": []}

if (calendar[current_date]["isHoliday"]):
    if (calendar[previous_date]["isHoliday"]):
        # Allocate 2 탕 근무자 (if there is a need)
        current_schedule = allocate_two_times(current_schedule, True, available_workers)
        # Filling in the remaining workers
        current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, [], True)
    elif (calendar[previous_date]["isTraining"]):
        # Filter for Planned Dates (latest previous day that is not training)
        planned_dates = {date: info for date, info in calendar.items() if info['isPlanned'] == True and info["isTraining"] == False}
        latest_previous_work_day = list(planned_dates.keys())[-1]
        prev_temp_schedule = open(f'./archive/json/{latest_previous_work_day}.json')
        prev_temp_schedule = json.load(prev_temp_schedule)
        if (calendar[latest_previous_work_day]["isHoliday"]):
            current_schedule = allocate_two_times(current_schedule, True, available_workers)
            # Filling in the remaining workers
            current_schedule = fill_remaining(current_schedule, available_workers, prev_temp_schedule, [], True)
        else:
            previous_kyohuan = list(set([i["name"] for i in prev_temp_schedule["members"] if i["workTime"] < 5]))
            current_schedule = allocate_two_times(current_schedule, True, available_workers)
            current_schedule = fill_remaining(current_schedule, available_workers, prev_temp_schedule, previous_kyohuan, False)
    else:
        # If yesterday was a work day
        previous_kyohuan = list(set([i["name"] for i in prev_schedule["members"] if i["workTime"] < 5]))
        print(previous_kyohuan)
        # Allocate 2 탕 근무자 (if there is a need)
        current_schedule = allocate_two_times(current_schedule, True, available_workers)
        # Filling in the remaining workers
        current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, previous_kyohuan, False)
    
elif (calendar[current_date]["isTraining"] == True):
    current_schedule = {"members": []}   

else:
    # Filter for Planned Dates (latest previous work day)
    planned_dates = {date: info for date, info in calendar.items() if info['isPlanned'] == True and info['isHoliday'] == False and info["isTraining"] == False}
    latest_previous_work_day = list(planned_dates.keys())[-1]
    prev_work_schedule = open(f'./archive/json/{latest_previous_work_day}.json')
    prev_work_schedule = json.load(prev_work_schedule)
    previous_kyohuan = list(set([i["name"] for i in prev_work_schedule["members"] if i["workTime"] < 5]))
    # Allocate Current Kyohuan
    # find exempted signal soldiers
    exempted_signal_soldiers = [worker["name"] for worker in exempted_workers if worker["ss"] == True]
    # current_schedule = allocate_current_kyohuan(exempted_signal_soldiers, prev_work_schedule)
    # # Allocate 2 탕 근무자 (if there is a need)
    # current_schedule = allocate_two_times(current_schedule, False, available_workers)
 
    # Filling in the remaining workers
    if (calendar[previous_date]["isHoliday"] == True):
        current_schedule = allocate_current_kyohuan(exempted_signal_soldiers, prev_schedule)
        current_schedule = allocate_two_times(current_schedule, False, available_workers)
        current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, [], True)
    elif (calendar[previous_date]["isTraining"] == True):
        # Filter for Planned Dates (latest previous day that is not training)
        planned_dates = {date: info for date, info in calendar.items() if info['isPlanned'] == True and info["isTraining"] == False}
        latest_previous_work_day = list(planned_dates.keys())[-1]
        prev_temp_schedule = open(f'./archive/json/{latest_previous_work_day}.json')
        prev_temp_schedule = json.load(prev_temp_schedule)
        if (calendar[latest_previous_work_day]["isHoliday"]):
            current_schedule = allocate_current_kyohuan(exempted_signal_soldiers, prev_temp_schedule)
            current_schedule = allocate_two_times(current_schedule, False, available_workers)
            # Filling in the remaining workers
            current_schedule = fill_remaining(current_schedule, available_workers, prev_temp_schedule, [], True)
        else:
            previous_kyohuan = list(set([i["name"] for i in prev_temp_schedule["members"] if i["workTime"] < 5]))
            current_schedule = allocate_current_kyohuan(exempted_signal_soldiers, prev_temp_schedule)
            current_schedule = allocate_two_times(current_schedule, False, available_workers)
            current_schedule = fill_remaining(current_schedule, available_workers, prev_temp_schedule, previous_kyohuan, False)
    else:
        current_schedule = allocate_current_kyohuan(exempted_signal_soldiers, prev_work_schedule)
        current_schedule = allocate_two_times(current_schedule, False, available_workers)
        current_schedule = fill_remaining(current_schedule, available_workers, prev_schedule, previous_kyohuan, False)


sorted_schedule = sorted(current_schedule["members"], key=sort_schedule)

formatted_sorted_schedule = {
    "members": sorted_schedule
}

json_object = json.dumps(formatted_sorted_schedule, indent=4, ensure_ascii=False)


with open(f"./archive/json/{current_date}.json", "w") as outfile:
    outfile.write(json_object)

calendar[current_date]['isPlanned'] = True

with open(f"./archive/timetable/january2024.json", 'w') as json_file:
    json.dump(calendar, json_file, indent=4)

two_point_db = json.load(open("./two_times.json"))
with open(f"./archive/two_point_db/{current_date}.json", "w") as outfile: 
        json.dump(two_point_db, outfile, indent=4, ensure_ascii=False)