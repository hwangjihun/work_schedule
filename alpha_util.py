import json
import random
from datetime import datetime
import pytz
from random_generator import RandomNumberGenerator

def array_diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

REST_LIST = [
    "채현우",
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

SIGNAL_SOLDIERS_LIST = [
    "허정현",
    "유창우",
    "김동수",
    "한철웅",
    "황지훈",
    "변희원"
]

def default_exemption(current_schedule_date):
    # Exemptions: 5대기, 휴가, 훈련, etc...
    # Based on 근무 DATE, check the people who are exempted from duty to the reasons above
    exempted_workers = []
    
    workers = json.load(open('workers.json'))["workers"]
    target_date = datetime.strptime(current_schedule_date, "%Y-%m-%d")

    # Specify the UTC timezone
    utc_tz = pytz.timezone('UTC')

    # Localize the target datetime to the UTC timezone
    target_date_utc = utc_tz.localize(target_date)

    # Convert the datetime to the KST timezone
    kst_tz = pytz.timezone('Asia/Seoul')
    current_kst_date = target_date_utc.astimezone(kst_tz)

    for worker in workers:
        if (worker["exempted_start_date"] == "na" and worker["exempted_end_date"] == "na"): 
            continue 
        else: 
            exempted_start_date = datetime.strptime(worker["exempted_start_date"], '%Y-%m-%d').astimezone(kst_tz)
            exempted_end_date = datetime.strptime(worker["exempted_end_date"], '%Y-%m-%d').astimezone(kst_tz)
            if (exempted_start_date <= current_kst_date <= exempted_end_date):
                exempted_workers.append(worker["name"])

    return exempted_workers

def rest_exemption(qualified_worker_count):
    # people who are entering rest
    FREE_OF_DUTY = []
    UPDATED_REST_QUEUE = []
    rest_file = open('rest.json')
    rest_data = json.load(rest_file)
    
    if (len(rest_data) < qualified_worker_count):
        rest_data.extend(REST_LIST)
    for idx, worker in enumerate(rest_data):
        if idx not in range(qualified_worker_count):
            UPDATED_REST_QUEUE.append(worker)
        else:
            FREE_OF_DUTY.append(worker)

    with open("rest.json", "w") as outfile: 
        json.dump(UPDATED_REST_QUEUE, outfile, indent=4, ensure_ascii=False)

    return FREE_OF_DUTY

def find_available_workers(current_schedule_date, calendar):
    workers_db = open("workers.json")
    workers_data = json.load(workers_db)

    # Find all the available workers on the day

    # available_workers --> ONLY EXCLUDES DEFAULT EXEMPTION ('휴가, etc')
    available_workers = []

    # final_available_workers --> EXCLUDES BOTH 비번 & default_exemption
    final_available_workers = []

    final_exempted_workers = []

    exempted_workers = default_exemption(current_schedule_date)
    
    for worker in workers_data["workers"]:
        if (worker["name"] in exempted_workers):
            final_exempted_workers.append(worker)
            continue
        else:
            available_workers.append(worker)
    
    # Working Day 비번 Criteria
    if (len(available_workers) > 10 and calendar[current_schedule_date]["isHoliday"] == False):
        exempted_workers = rest_exemption(len(available_workers) - 10)
        for worker in available_workers:
            if (worker["name"] in exempted_workers):
                final_exempted_workers.append(worker)
                continue
            else:
                final_available_workers.append(worker)  
    elif (len(available_workers) > 12 and calendar[current_schedule_date]["isHoliday"] == True):
        exempted_workers = rest_exemption(len(available_workers) - 12)
        for worker in available_workers:
            if (worker["name"] in exempted_workers):
                final_exempted_workers.append(worker)
                continue
            else:
                final_available_workers.append(worker)
    else:
        final_available_workers = available_workers
    workers_db.close()
    return [final_available_workers, final_exempted_workers]

def allocate_current_kyohuan(exempted_signal_soldiers, yesterday_data):
    
    # Need to check in default_exemption and rest_exemption
    CURRENT_KYOHUAN = []
    visited = []
    SIGNAL_SOLDIERS = list(json.load(open('kyohuan.json')))
    SIGNAL_SOLDIERS_EXCLUDING_EXEMPTED = [worker for worker in [soldier for soldier in SIGNAL_SOLDIERS if soldier not in visited] if worker not in exempted_signal_soldiers]
    if (len(SIGNAL_SOLDIERS_EXCLUDING_EXEMPTED) < 2):
        SIGNAL_SOLDIERS.extend(SIGNAL_SOLDIERS_LIST)
    for soldier in SIGNAL_SOLDIERS:
        if (len(CURRENT_KYOHUAN) == 2):
            break
        if (soldier not in exempted_signal_soldiers):
            print(soldier)
            CURRENT_KYOHUAN.append(soldier)
        visited.append(soldier)

    for worker in visited:
        SIGNAL_SOLDIERS.remove(worker)
    print(f"current kyohuan: {CURRENT_KYOHUAN}")
    with open("kyohuan.json", "w") as outfile: 
        json.dump(SIGNAL_SOLDIERS, outfile, indent=4, ensure_ascii=False)

    updated_schedule = {"members": []}
    prev_final_time_worker = list(filter(lambda worker: worker['workTime'] == 12, yesterday_data["members"]))
    if (prev_final_time_worker[0]['name'] in CURRENT_KYOHUAN):
        bfr_lunch_worker = array_diff(CURRENT_KYOHUAN, [prev_final_time_worker[0]['name']])
        updated_schedule["members"].append({
            "name": bfr_lunch_worker[0],
            "workTime": 1
        })
        updated_schedule["members"].append({
            "name": bfr_lunch_worker[0],
            "workTime": 2
        })
        updated_schedule["members"].append({
            "name": prev_final_time_worker[0]['name'],
            "workTime": 3
        })
        updated_schedule["members"].append({
            "name": prev_final_time_worker[0]['name'],
            "workTime": 4
        })
    else:
        for idx, member in enumerate(CURRENT_KYOHUAN):
            updated_schedule["members"].append({
                "name": member,
                "workTime": idx * 2 + 1
            })
            updated_schedule["members"].append({
                "name": member,
                "workTime":  idx * 2 + 2
            })
    return updated_schedule

def two_times(required_ppl_count, available_workers):
    # People to allocate
    TWO_TIMES_DUTY = []
    # POINTS_DB --> two times point db
    POINTS_DB = json.load(open('two_times.json'))
    
    # Get POINTS_DB which excludes people who are exempted from duty 
    POINTS_DB_EXCLUDED = {}
    for worker, points in POINTS_DB.items():
        if (worker not in available_workers):
            continue 
        else:
            POINTS_DB_EXCLUDED[str(worker)] = int(points)

    # DOWN STAIRCASE ALGO
    while len(TWO_TIMES_DUTY) != required_ppl_count:
        least_point = min([points for worker, points in POINTS_DB_EXCLUDED.items() if worker not in TWO_TIMES_DUTY])
        unlucky_worker = random.choice([worker for worker, points in POINTS_DB_EXCLUDED.items() if points == least_point and worker not in TWO_TIMES_DUTY])
        TWO_TIMES_DUTY.append(unlucky_worker)
        POINTS_DB_EXCLUDED[str(unlucky_worker)] += 1
        POINTS_DB[str(unlucky_worker)] += 1
    
    print(f"Two times duty: {TWO_TIMES_DUTY}")
    with open("two_times.json", "w") as outfile: 
        json.dump(POINTS_DB, outfile, indent=4, ensure_ascii=False)
    return TWO_TIMES_DUTY

def allocate_two_times(current_schedule, rest_day, available_workers):
    DAYTIME = []
    NIGHTTIME = []
    if (rest_day is True):
        DAYTIME = [i for i in range(1, 8)]
        NIGHTTIME = [i for i in range(8, 13)]
    else:
        DAYTIME = [i for i in range(5, 8)]
        NIGHTTIME = [i for i in range(8, 13)]
    missing_timings = array_diff([i for i in range(1, 13)],  [worker["workTime"] for worker in current_schedule["members"]])
    check_free_peeps = array_diff([i["name"] for i in available_workers], [worker["name"] for worker in current_schedule["members"]])
    print(f'CUrrent schedule after kyohuan: {current_schedule}')
    print(f'FRee peeps after kyohuan: {check_free_peeps}')
    # Check if there is more 근무 OR if there is more free people
    ttd_filled_dt = []
    ttd_filled_nt = []

    two_times_chosen_workers = []

    if (len(check_free_peeps) < len(missing_timings)):
        two_times_duty = two_times(len(missing_timings) - len(check_free_peeps), check_free_peeps)
        print(two_times_duty)
        for two_times_worker in two_times_duty:

            while True:
                RANDOM_DAYTIME = random.choice(DAYTIME)
                RANDOM_NIGHTTIME = random.choice(NIGHTTIME)

                if (RANDOM_DAYTIME not in ttd_filled_dt and RANDOM_NIGHTTIME not in ttd_filled_nt):
                    break
            two_times_chosen_workers.append(two_times_worker)
            current_schedule["members"].append({
                "name": two_times_worker,
                "workTime": RANDOM_DAYTIME
            })
            current_schedule["members"].append({
                "name": two_times_worker,
                "workTime": RANDOM_NIGHTTIME
            })
            ttd_filled_dt.append(RANDOM_DAYTIME)
            ttd_filled_nt.append(RANDOM_NIGHTTIME)

    return current_schedule 

def fill_remaining(current_schedule, available_workers, previous_schedule, previous_kyohuan, isHoliday):
    missing_timings = array_diff([i for i in range(1, 13)],  [worker["workTime"] for worker in current_schedule["members"]])
    check_free_peeps = array_diff([i["name"] for i in available_workers], [worker["name"] for worker in current_schedule["members"]])
 
    print(f"check free peeps at fill remaining{check_free_peeps}")
    DAYTIME = [timeid for timeid in missing_timings if timeid in range(1, 8)]
    NIGHTTIME = [timeid for timeid in missing_timings if timeid in range(8, 13)]
    
    rng_day = RandomNumberGenerator(choices=DAYTIME)
    rng_night = RandomNumberGenerator(choices=NIGHTTIME)
    
    # Filters out previous kyohuan and two times 근무 from yesterday
    two_times_dict = {}
    two_times_duty_prev = []

    # Could be weekends yesterday
    if (isHoliday):
        for member in previous_schedule["members"]:
            if (member["name"] in list(two_times_dict.keys())):
                two_times_dict[member["name"]] += 1
            else:
                two_times_dict[member["name"]] = 1
        
    elif (isHoliday is False):
        for member in previous_schedule["members"]:
            if (member["workTime"] < 5):
                continue 
            else:
                if (member["name"] in list(two_times_dict.keys())):
                    two_times_dict[member["name"]] += 1
                else:
                    two_times_dict[member["name"]] = 1

    max_count_two_times = max(list(two_times_dict.values()))
    print(f"two_times_dict {two_times_dict}")
    if (max_count_two_times > 1):
        for member, count in two_times_dict.items(): 
            if (count != 1):
                two_times_duty_prev.append(str(member))    
    print(f"two_times_duty_previous {two_times_duty_prev}")
    
    filtered_previous_schedule = []
    if (isHoliday):
        for member in previous_schedule["members"]:
            if (member["name"] in check_free_peeps):
                if (member["name"] in two_times_duty_prev):
                    continue
                else:
                    filtered_previous_schedule.append(member)
    elif (isHoliday is False):
        for member in previous_schedule["members"]:
            if (member["name"] in check_free_peeps):
                if (member["name"] in previous_kyohuan or member["name"] in two_times_duty_prev):
                    continue
                else:
                    filtered_previous_schedule.append(member)
    for member in filtered_previous_schedule:
        # Check if yesterday's 근무 WAS NIGHT
        if (member["workTime"] in range(8, 13)):
            random_dt = rng_day.generate_random_number()
            if (random_dt is None):
                continue
            current_schedule["members"].append({
                "name": member["name"],
                "workTime": random_dt
            })
        # Check if yesterday's 근무 WAS DAY
        elif (member["workTime"] in range(1, 8)):
            random_nt = rng_night.generate_random_number()
            if (random_nt is None):
                continue
            current_schedule["members"].append({
                "name": member["name"],
                "workTime": random_nt
            })
    # If there's still remaining people, randomly slot them in 
    missing_timings = array_diff([i for i in range(1, 13)],  [worker["workTime"] for worker in current_schedule["members"]])
    check_free_peeps = array_diff([i["name"] for i in available_workers], [worker["name"] for worker in current_schedule["members"]])
    if (len(missing_timings) != 0):
        random.shuffle(missing_timings)
        random.shuffle(check_free_peeps)
        for mt, cfp in zip(missing_timings, check_free_peeps):
            current_schedule["members"].append({
                "name": cfp,
                "workTime": mt
            })
    return current_schedule