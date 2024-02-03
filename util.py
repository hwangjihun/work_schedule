import json
from datetime import datetime, timedelta
import random

WORKERS_LIST = [
    "허정현",
    "유창우",
    "전성현",
    "김동수",
    "한철웅",
    "민준식",
    "김태언",
    "최선웅",
    "황지훈",
    "변희원"
]

def array_diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def default_exemption(current_schedule_date):
    exempted_workers = []
    workers = json.load(open('workers.json'))["workers"]
    target_date = datetime.strptime(current_schedule_date, "%Y-%m-%d")

    for worker in workers:
        if (worker["exempted_start_date"] == "na" and worker["exempted_end_date"] == "na"): 
            continue 
        else: 
            for exempted_start_date, exempted_end_date in zip(worker["exempted_start_date"], worker["exempted_end_date"]):
                exempted_start_date = datetime.strptime(exempted_start_date, '%Y-%m-%d')
                exempted_end_date = datetime.strptime(exempted_end_date, '%Y-%m-%d')
                if (exempted_start_date <= target_date <= exempted_end_date):
                    exempted_workers.append(worker["name"])

    return exempted_workers

def rest_exemption(qualified_worker_count):
    # people who are entering rest
    FREE_OF_DUTY = []
    UPDATED_REST_QUEUE = []
    rest_file = open('rest.json')
    rest_data = json.load(rest_file)
    
    if (len(rest_data) < qualified_worker_count):
        rest_data.extend(WORKERS_LIST)
    for idx, worker in enumerate(rest_data):
        if idx not in range(qualified_worker_count):
            UPDATED_REST_QUEUE.append(worker)
        else:
            FREE_OF_DUTY.append(worker)

    with open("rest.json", "w") as outfile: 
        json.dump(UPDATED_REST_QUEUE, outfile, indent=4, ensure_ascii=False)

    return FREE_OF_DUTY

def find_available_workers(current_schedule_date, calendar):
    previous_date = datetime.strptime(current_schedule_date, '%Y-%m-%d') - timedelta(days=1)
    previous_date = datetime.strftime(previous_date, '%Y-%m-%d')

    workers_db = open("workers.json")
    workers_data = json.load(workers_db)
    available_workers = []
    final_available_workers = []
    exempted_workers = default_exemption(current_schedule_date)
    try:
        yesterday_data = json.load(open(f"./archive/json/{previous_date}.json"))
        yesterday_dangjik = list(filter(lambda worker: worker['workTime'] == 6, yesterday_data["members"]))[0]["name"]
    except:
        yesterday_dangjik = ""
    
    for worker in workers_data["workers"]:
        if (worker["name"] in exempted_workers or worker["name"] == yesterday_dangjik):
            continue
        else:
            available_workers.append(worker["name"])
    resting_workers = rest_exemption(len(available_workers) - 6)
    for worker in available_workers:
        if worker in resting_workers:
            continue
        else:
            final_available_workers.append(worker)
    return final_available_workers

def dangjik(available_workers):

    CURRENT_DANGJIK = ""
    visited = []
    workers = list(json.load(open('dangjik.json')))
    
    if (len(workers) < 1):
        workers.extend(WORKERS_LIST)
    for soldier in workers:
        if (CURRENT_DANGJIK != ""):
            break
        if (soldier in available_workers):
            CURRENT_DANGJIK = soldier
        visited.append(soldier)
    for worker in visited:
        workers.remove(worker)
    with open("dangjik.json", "w") as outfile: 
        json.dump(workers, outfile, indent=4, ensure_ascii=False)

    updated_schedule = {"members": [
        {
            "name": CURRENT_DANGJIK,
            "workTime": 6
        }
    ]}

    return updated_schedule

def fill_remaining(current_schedule, available_workers):
    missing_timings = array_diff([i for i in range(1, 7)],  [worker["workTime"] for worker in current_schedule["members"]])
    check_free_peeps = array_diff([i for i in available_workers], [worker["name"] for worker in current_schedule["members"]])
    random.shuffle(missing_timings)
    random.shuffle(check_free_peeps)
    for mt, cfp in zip(missing_timings, check_free_peeps):
        current_schedule["members"].append({
            "name": cfp,
            "workTime": mt
        })
    return current_schedule