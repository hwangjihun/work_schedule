import json, random

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

def default_exemption():
    # Default exemptions: 5대기, 휴가
    # Add workers to exempted.json
    workers_db = open('workers.json')
    workers_data = json.load(workers_db)["workers"]
    return [worker["name"] for worker in workers_data if worker["exempted"] == True]

def two_times(next_kyohuan, required_ppl_count):
    # Two Times Point System
    two_times_list = open('two_times.json')
    two_times_list = json.load(two_times_list)
    ttl_excluding_kyohuan = {}

    # People going into two_times_duty on the new date
    two_times_duty = []

    # Exclude those who r in kyohuan
    for worker, desc in two_times_list.items():
        if (worker in next_kyohuan):
            continue
        else:
            ttl_excluding_kyohuan[str(worker)] = {"two_times_count": int(desc["two_times_count"])}

    # To make it fair, this will be a point system
    
    least_point = 0

    for i in range(required_ppl_count):
        least_point = min([worker["two_times_count"] for worker in ttl_excluding_kyohuan.values()])
        # ttd stands for two times duty

        # Two times duty to randomize (cuz there might be more than one person with the same points)
        ttd_to_randomize = {}
        
        for worker, desc in ttl_excluding_kyohuan.items():
            if (desc["two_times_count"] == least_point):
                ttd_to_randomize[worker] = desc 
        
        unlucky_boi = random.choice(list(ttd_to_randomize.keys()))
        two_times_duty.append(unlucky_boi)
        # Awarded one point for doing two time
        ttl_excluding_kyohuan[unlucky_boi]["two_times_count"] += 1
        two_times_list[unlucky_boi]["two_times_count"] += 1
    print(ttl_excluding_kyohuan)
    print(two_times_list)
    with open("two_times.json", "w") as outfile: 
        json.dump(two_times_list, outfile, indent=4, ensure_ascii=False)
    return two_times_duty
two_times(["황지훈", "김태언"], 1)