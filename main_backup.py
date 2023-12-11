# WEEKDAY PROGRAM GENERATION (INCLUDES EDGE CASES)

import json, random
from exempted_workers import rest_exemption, default_exemption

def array_diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

# Load Previous Day's 근무 & Current Workers DB
prev_db = open('previous_db.json')
workers_db = open('workers.json')
prev_data = json.load(prev_db)
workers_data = json.load(workers_db)

# Today's available workers excluding 비번 (if there is) & default_exemption
available_workers = []
final_available_workers = []

exempted_default = default_exemption()
for worker in workers_data["workers"]:
    if (worker["name"] in exempted_default):
        continue
    else:
        available_workers.append(worker)

if (len(available_workers) > 10):
    exempted_workers = rest_exemption(len(available_workers))
    for worker in available_workers:
        if (worker["name"] in exempted_workers):
            continue
        else:
            final_available_workers.append(worker)  
else:
    final_available_workers = available_workers

# Attaining the next members for 오전 & 오후 교환
# Logic: See previous day's shift and exempt them from today's shift

# 1. Get previous day workers who did 오전 & 오후 교환
previous_kyohuan = list(set([i["name"] for i in prev_data["members"] if i["workTime"] < 5]))

# 2. Get all current signal soldiers excluding yesterday's 오전 & 오후 교환
current_signal_soldiers = list([i["name"] for i in final_available_workers if i["ss"] is True and i["name"] not in previous_kyohuan])

# Super weird edge case that might happen?? when there is not enough signal soldiers, and i have to put the same person on
# the previous day
# if (len(current_signal_soldiers) < 2): (account for this minor issue later)

# 3. Randomize people to 오전 & 오후 교환
next_kyohuan = []
while len(next_kyohuan) < 2:
    random_soldier = random.choice(current_signal_soldiers)
    if random_soldier in next_kyohuan:
        continue
    else:
        next_kyohuan.append(random_soldier)

updated_schedule = {"members": []}

for idx, member in enumerate(next_kyohuan):
    updated_schedule["members"].append({
        "name": member,
        "workTime": idx * 2 + 1,
        "signalSoldier": True
    })
    updated_schedule["members"].append({
        "name": member,
        "workTime":  idx * 2 + 2,
        "signalSoldier": True
    })
# print(f"Final available workers: {final_available_workers}")

final_available_names = [worker["name"] for worker in final_available_workers]
for member in prev_data["members"]:
    if (member["name"] in previous_kyohuan or member["name"] in next_kyohuan or member["name"] not in final_available_names):
        continue
    else: 
        if member["workTime"] > 4:
            if member["workTime"] + 5 > 12:
                updated_schedule["members"].append({
                    "name": member["name"],
                    "workTime": ((member["workTime"] + 5) % 10) + 2,
                    "signalSoldier": member["signalSoldier"]
                })
            else:
                updated_schedule["members"].append({
                    "name": member["name"],
                    "workTime": member["workTime"] + 5,
                    "signalSoldier": member["signalSoldier"]
                })
    
missing_timings = array_diff([i for i in range(1, 13)],  [worker["workTime"] for worker in updated_schedule["members"]])

check_free_peeps = array_diff([i["name"] for i in final_available_workers], [worker["name"] for worker in updated_schedule["members"]])

# How to randomly allocate the missing timings??
random.shuffle(check_free_peeps)

for mt, cfp in zip(missing_timings, check_free_peeps):
    updated_schedule["members"].append({
        "name": cfp,
        "workTime": mt,
        "signalSoldier": True
    })

json_object = json.dumps(updated_schedule, indent=4, ensure_ascii=False)
with open("new_db.json", "w") as outfile:
    outfile.write(json_object)