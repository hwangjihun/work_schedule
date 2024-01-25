import json
from util import (
    default_exemption, 
    rest_exemption,
    find_available_workers
)

calendar = json.load(open("./2024.json"))

unplanned_dates = list({date: info for date, info in calendar.items() if info['isPlanned'] == False}.keys())
current_date = unplanned_dates[0]

available_workers = find_available_workers(current_date, calendar)