# IDEAL SITUATION where we have no edge cases (Base Program)

import json, random

def array_diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

# Load Previous Day's 근무
f = open('previous_db.json')
f2 = open('workers.json')
data = json.load(f)
workers = json.load(f2)

# Randomizing the next members for 오전 & 오후 교환
# Logic: See previous day's shift and exempt them from today's shift

# 1. Get previous day members who did 오전 & 오후 교환
previous_members = list(set([i["name"] for i in data["members"] if i["workTime"] < 5]))

# 2. Get all current signal soldiers excluding yesterday's 오전 & 오후 교환
current_signal_soldiers = list([i["name"] for i in workers["workers"] if i["ss"] is True and i["name"] not in previous_members])

# 3. Randomize people to assign to 오전 & 오후 교환
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

for member in data["members"]:
    if (member["name"] in previous_members or member["name"] in next_kyohuan):
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

check_free_peeps = array_diff([i["name"] for i in workers["workers"]], [worker["name"] for worker in updated_schedule["members"]])
print(missing_timings)
print(check_free_peeps)

# How to randomly allocate the missing timings??

# f.close()

# Serializing json
json_object = json.dumps(updated_schedule, indent=4, ensure_ascii=False)
# json_object = json.dumps(data, indent=4, ensure_ascii=False)
# Writing to sample.json
with open("sample.json", "w") as outfile:
    outfile.write(json_object)