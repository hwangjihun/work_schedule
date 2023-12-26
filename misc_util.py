import json, random
from os import listdir
from os.path import isfile, join, splitext
from datetime import datetime, timedelta
import pytz
from random_generator import RandomNumberGenerator

def array_diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

REST_LIST = [
                {
                    "name": "김동수"
                },
                {
                    "name": "김태언"
                },
                {
                    "name": "황지훈"
                },
                {
                    "name": "채현우"
                },
                {
                    "name": "최진영"
                }
            ]

def find_previous_schedule():
    schedule_path = './archive/json'
    schedule_dates = [f for f in listdir(schedule_path) if isfile(join(schedule_path, f))]
    schedule_dates = [splitext(date)[0] for date in schedule_dates]
    return max([datetime.strptime(date, '%Y-%m-%d') for date in schedule_dates]).strftime('%Y-%m-%d')

def set_current_schedule_date():
    # Search for latest_date 
    my_path = './archive/json'
    file_dates = [f for f in listdir(my_path) if isfile(join(my_path, f))]

    if (len(file_dates) == 0):
         # Set the timezone to KST
        kst_timezone = pytz.timezone('Asia/Seoul')

        # Get the current time in KST
        current_time_kst = datetime.now(kst_timezone)
        return current_time_kst.strftime('%Y-%m-%d')
    
    else:
        file_dates = [splitext(date)[0] for date in file_dates]
        file_dates = [datetime.strptime(date, '%Y-%m-%d') for date in file_dates]
        next_day = max(file_dates) + timedelta(days=1)
        return next_day.strftime('%Y-%m-%d')

def default_exemption():
    # Exemptions: 5대기, 휴가, 훈련, etc...
    # Based on 근무 DATE, check the people who are exempted from duty to the reasons above
    exempted_workers = []
    
    workers = json.load(open('workers.json'))["workers"]
    current_schedule_date = set_current_schedule_date()
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
def test_find_available_workers(current_schedule_date):
    workers_db = open('workers.json')
    workers_data = json.load(workers_db)

    # Find all the available workers on the day

    # available_workers --> ONLY EXCLUDES DEFAULT EXEMPTION ('휴가, etc')
    available_workers = []

    # final_available_workers --> EXCLUDES BOTH 비번 & default_exemption
    final_available_workers = []

    exempted_workers = default_exemption()
    
    for worker in workers_data["workers"]:
        if (worker["name"] in exempted_workers):
            continue
        else:
            available_workers.append(worker)

    # Weekday 비번 Criteria
    if (len(available_workers) > 10 and datetime.strptime(current_schedule_date, "%Y-%m-%d").weekday() < 5):
        exempted_workers = rest_exemption(len(available_workers))
        for worker in available_workers:
            if (worker["name"] in exempted_workers):
                continue
            else:
                final_available_workers.append(worker)  
    else:
        final_available_workers = available_workers

    workers_db.close()
    return final_available_workers

def find_available_workers():
    workers_db = open('workers.json')
    workers_data = json.load(workers_db)

    # Find all the available workers on the day

    # available_workers --> ONLY EXCLUDES DEFAULT EXEMPTION ('휴가, etc')
    available_workers = []

    # final_available_workers --> EXCLUDES BOTH 비번 & default_exemption
    final_available_workers = []

    exempted_workers = default_exemption()
    
    for worker in workers_data["workers"]:
        if (worker["name"] in exempted_workers):
            continue
        else:
            available_workers.append(worker)

    current_schedule_date = set_current_schedule_date()

    # Weekday 비번 Criteria
    if (len(available_workers) > 10 and datetime.strptime(current_schedule_date, "%Y-%m-%d").weekday() < 5):
        exempted_workers = rest_exemption(len(available_workers))
        for worker in available_workers:
            if (worker["name"] in exempted_workers):
                continue
            else:
                final_available_workers.append(worker)  
    else:
        final_available_workers = available_workers

    workers_db.close()
    return final_available_workers

def rest_exemption(avail_workers):
    # 비번 (for this to come true, there must not be anyone who does two shifts in a day)
    # aka there must be exactly 10 unique workers during weekdays and
    # 12 unique workers during weekends for someone to get a 비번

    # Putting it as a separate function from the rest such as 
    # 휴가, 5대기, etc.. due to it not being a must to be exempted
    rest_file = open('rest.json')
    rest_data = json.load(rest_file)["rest"]
    overwrite_data = rest_data
    updated_duty_queue = []

    # If the rest queue is smaller than the number of workers who are free, 
    # then extend a new set of 비번
    if (len(rest_data) < avail_workers - 10):
        overwrite_data.extend(REST_LIST)
    free_of_duty = []
    for idx, worker in enumerate(overwrite_data):
        if idx not in range(avail_workers-10):
            updated_duty_queue.append(worker)
        else:
            free_of_duty.append(worker["name"])
    overwrite_data = {
        "rest" : updated_duty_queue
    }
    overwrite_data = json.dumps(overwrite_data, indent=4, ensure_ascii=False)
    with open("rest.json", "w") as outfile:
        outfile.write(overwrite_data)

    rest_file.close()
    return free_of_duty


def two_times(next_kyohuan, required_ppl_count):
    # Two Times Point System
    two_times_list = open('two_times.json')
    two_times_list = json.load(two_times_list)
    ttl_excluding_kyohuan = {}

    # People going into two_times_duty on the new date
    two_times_duty = []

    # Exclude those who r in kyohuan & 열외
    for worker, desc in two_times_list.items():
        if (worker in next_kyohuan or worker in default_exemption()):
            continue
        else:
            ttl_excluding_kyohuan[str(worker)] = {"two_times_count": int(desc["two_times_count"])}

    # To make it fair, this will be a point system
    
    least_point = 0

    while len(two_times_duty) != required_ppl_count:
        least_point = min([worker["two_times_count"] for worker in ttl_excluding_kyohuan.values()])
        # ttd stands for two times duty

        # Two times duty to randomize (cuz there might be more than one person with the same points)
        ttd_to_randomize = {}
        
        for worker, desc in ttl_excluding_kyohuan.items():
            if (desc["two_times_count"] == least_point):
                ttd_to_randomize[worker] = desc 
        
        unlucky_boi = random.choice(list(ttd_to_randomize.keys()))
        # Collision problem
        if (unlucky_boi in two_times_duty):
            continue

        two_times_duty.append(unlucky_boi)
        
        # Awarded one point for doing two time
        ttl_excluding_kyohuan[unlucky_boi]["two_times_count"] += 1
        two_times_list[unlucky_boi]["two_times_count"] += 1

    # for i in range(required_ppl_count):
    #     least_point = min([worker["two_times_count"] for worker in ttl_excluding_kyohuan.values()])
    #     # ttd stands for two times duty

    #     # Two times duty to randomize (cuz there might be more than one person with the same points)
    #     ttd_to_randomize = {}
        
    #     for worker, desc in ttl_excluding_kyohuan.items():
    #         if (desc["two_times_count"] == least_point):
    #             ttd_to_randomize[worker] = desc 
        
    #     unlucky_boi = random.choice(list(ttd_to_randomize.keys()))
    #     two_times_duty.append(unlucky_boi)
    #     # Awarded one point for doing two time
    #     ttl_excluding_kyohuan[unlucky_boi]["two_times_count"] += 1
    #     two_times_list[unlucky_boi]["two_times_count"] += 1

  

    with open("two_times.json", "w") as outfile: 
        json.dump(two_times_list, outfile, indent=4, ensure_ascii=False)
    return two_times_duty


def allocate_current_kyohuan(prev_data, available_workers):
    next_kyohuan = []
    previous_kyohuan = []
    if (len(prev_data)) == 0:
        current_signal_soldiers = list([i["name"] for i in available_workers if i["ss"] is True])
        while len(next_kyohuan) < 2:
            random_soldier = random.choice(current_signal_soldiers)
            if random_soldier in next_kyohuan:
                continue
            else:
                next_kyohuan.append(random_soldier)
    else:
        # Attaining the next members for 오전 & 오후 교환
        # Logic: See previous day's shift and exempt them from today's shift
        
        # 1. Get previous day workers who did 오전 & 오후 교환
        previous_kyohuan = list(set([i["name"] for i in prev_data["members"] if i["workTime"] < 5]))
        
        # 2. Get all current signal soldiers excluding yesterday's 오전 & 오후 교환
        current_signal_soldiers = list([i["name"] for i in available_workers if i["ss"] is True and i["name"] not in previous_kyohuan])
    
        # 3. Randomize people to 오전 & 오후 교환
        while len(next_kyohuan) < 2:
            random_soldier = random.choice(current_signal_soldiers)
            if random_soldier in next_kyohuan:
                continue
            else:
                next_kyohuan.append(random_soldier)

    updated_schedule = {"members": []}

    # Ensure that the previous day's 막번 does not go into 오전 교환
    # (only if the 막번 is a signal soldier)

    prev_final_time_worker = list(filter(lambda worker: worker['workTime'] == 12, prev_data["members"]))
    if (prev_final_time_worker[0]['name'] in next_kyohuan):
        bfr_lunch_worker = array_diff(next_kyohuan, [prev_final_time_worker[0]['name']])
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
        for idx, member in enumerate(next_kyohuan):
            updated_schedule["members"].append({
                "name": member,
                "workTime": idx * 2 + 1
            })
            updated_schedule["members"].append({
                "name": member,
                "workTime":  idx * 2 + 2
            })
    return [next_kyohuan, updated_schedule, previous_kyohuan]

def allocate_two_times(current_schedule, available_workers, next_kyohuan, weekends_):
    DAYTIME = []
    NIGHTTIME = []
    if (weekends_ is True):
        DAYTIME = [i for i in range(1, 8)]
        NIGHTTIME = [i for i in range(8, 13)]
    else:
        DAYTIME = [i for i in range(5, 8)]
        NIGHTTIME = [i for i in range(8, 13)]
    missing_timings = array_diff([i for i in range(1, 13)],  [worker["workTime"] for worker in current_schedule["members"]])
    check_free_peeps = array_diff([i["name"] for i in available_workers], [worker["name"] for worker in current_schedule["members"]])
  
    # Check if there is more 근무 OR if there is more free people
    ttd_filled_dt = []
    ttd_filled_nt = []

    two_times_chosen_workers = []

    if (len(check_free_peeps) < len(missing_timings)):
        two_times_duty = two_times(next_kyohuan, len(missing_timings) - len(check_free_peeps))
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
    print(current_schedule)
    return current_schedule 

def fill_remaining(current_schedule, available_workers, previous_schedule, previous_kyohuan):
    missing_timings = array_diff([i for i in range(1, 13)],  [worker["workTime"] for worker in current_schedule["members"]])
    check_free_peeps = array_diff([i["name"] for i in available_workers], [worker["name"] for worker in current_schedule["members"]])
    
    DAYTIME = [timeid for timeid in missing_timings if timeid in range(1, 8)]
    NIGHTTIME = [timeid for timeid in missing_timings if timeid in range(8, 13)]
    
    rng_day = RandomNumberGenerator(choices=DAYTIME)
    rng_night = RandomNumberGenerator(choices=NIGHTTIME)
    
    # FIlters out previous kyohuan and two times 근무 from yesterday
    two_times_dict = {}
    two_times_duty_prev = []
    for member in previous_schedule["members"]:
        if (member["workTime"] < 5):
            continue
        else:
            if (member["name"] in list(two_times_dict.keys())):
                two_times_dict[member["name"]] += 1
            else:
                two_times_dict[member["name"]] = 1
    max_count_two_times = max(list(two_times_dict.values()))

    if (max_count_two_times > 1):
        for member, count in two_times_dict.items(): 
            if (count != 1):
                two_times_duty_prev.append(str(member))    

    filtered_previous_schedule = []
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