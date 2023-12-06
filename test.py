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

print(next_kyohuan)

f.close()