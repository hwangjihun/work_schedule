import json, random

f = open('previous_db.json')
data = json.load(f)

# Randomizing the next members for 1, 2, 3, 4

# 1. Get previous day members who did 1, 2, 3, 4
previous_members = list(set([i["name"] for i in data["members"] if i["workTime"] < 5]))

# 2. Get all current signal soldiers
current_signal_soldiers = list(set([i["name"] for i in data["members"] if i["signalSoldier"] is True and i["name"] not in previous_members])) 

# 3. Randomize people to assign to 1, 2, 3, 4
next_kyohuan = []
while len(next_kyohuan) < 2:
    random_soldier = random.choice(current_signal_soldiers)
    if random_soldier in next_kyohuan:
        continue
    else:
        next_kyohuan.append(random_soldier)

for idx, member in enumerate(data["members"]): 
    if (member["workTime"] <= 4):
        del data["members"][idx]
        
print(data)

# updated_schedule = {"members": []}

# for idx, soldier in enumerate(next_kyohuan):
#     updated_schedule["members"].append({
#         "name": soldier,
#         "workTime": idx * 2 + 1,
#         "signalSoldier": True
#     })
#     updated_schedule["members"].append({
#         "name": soldier,
#         "workTime":  idx * 2 + 2,
#         "signalSoldier": True
#     })
#     for member in data["members"]:
#         if (member[""])
    
# 5. Normal 근무자 (goes down by 5)

# ** Exclude members in kyohuan and include previous kyohuan


# for member in data["members"]:
#     if (member["workTime"] > 4):
#         if member["workTime"] + 5 > 12:
#             updated_schedule["members"].append({
#                 "name": member["name"],
#                 "workTime": (member["workTime"] + 5 % 10) + 2,
#                 "signalSoldier": member["signalSoldier"]
#             })
#         else:
#             updated_schedule["members"].append({
#                 "name": member["name"],
#                 "workTime": member["workTime"] + 5,
#                 "signalSoldier": member["signalSoldier"]
#             })
f.close()

# Serializing json
# json_object = json.dumps(updated_schedule, indent=4, ensure_ascii=False)
# json_object = json.dumps(data, indent=4, ensure_ascii=False)
# Writing to sample.json
# with open("sample.json", "w") as outfile:
#     outfile.write(json_object)