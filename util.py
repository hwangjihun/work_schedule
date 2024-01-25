import json
from datetime import datetime, timedelta

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

def default_exemption(current_schedule_date):
    exempted_workers = []
    workers = json.load(open('workers.json'))["workers"]
    target_date = datetime.strptime(current_schedule_date, "%Y-%m-%d")

    for worker in workers:
        if (worker["exempted_start_date"] == "na" and worker["exempted_end_date"] == "na"): 
            continue 
        else: 
            exempted_start_date = datetime.strptime(worker["exempted_start_date"], '%Y-%m-%d')
            exempted_end_date = datetime.strptime(worker["exempted_end_date"], '%Y-%m-%d')
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
    yesterday_data = json.load(open(f"./archive/json/{previous_date}.json"))
    yesterday_dangjik = list(filter(lambda worker: worker['workTime'] == 6, yesterday_data["members"]))[0]["name"]
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
    print(visited)
    for worker in visited:
        workers.remove(worker)
    print(f"current dangjik: {CURRENT_DANGJIK}")
    with open("dangjik.json", "w") as outfile: 
        json.dump(workers, outfile, indent=4, ensure_ascii=False)

    return CURRENT_DANGJIK
