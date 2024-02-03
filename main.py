import json
from util import (
    find_available_workers,
    dangjik,
    fill_remaining
)

def sort_schedule(x): 
    return int(x["workTime"])

calendar = json.load(open("./2024.json"))

unplanned_dates = list({date: info for date, info in calendar.items() if info['isPlanned'] == False}.keys())
current_date = unplanned_dates[0]

available_workers = find_available_workers(current_date, calendar)

current_schedule = {"members": []}

current_schedule = dangjik(available_workers)

current_schedule = fill_remaining(current_schedule, available_workers)

sorted_schedule = sorted(current_schedule["members"], key=sort_schedule)

formatted_sorted_schedule = {
    "members": sorted_schedule
}

json_object = json.dumps(formatted_sorted_schedule, indent=4, ensure_ascii=False)

with open(f"./archive/json/{current_date}.json", "w") as outfile:
    outfile.write(json_object)

calendar[current_date]['isPlanned'] = True

with open(f"./2024.json", 'w') as json_file:
    json.dump(calendar, json_file, indent=4)
