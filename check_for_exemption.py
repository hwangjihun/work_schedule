import json

REST_LIST = [
                {
                    "name": "김동수"
                },
                {
                    "name": "한철웅"
                },
                {
                    "name": "황지훈"
                },
                {
                    "name": "변희원"
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
    # Check if there's no one left first on the 비번 list.
    # If there is no one, then insert a new set based on 짬

    # avail_workers
    # This parameter is the number of available unique workers on that day

    if len(rest_data) == 0:
        new_set = {
           "rest": REST_LIST
        }

        new_set = json.dumps(new_set, indent=4, ensure_ascii=False)

        with open("rest.json", "w") as outfile:
            outfile.write(new_set)
    else:
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
                free_of_duty.append(worker)
        overwrite_data = {
            "rest" : updated_duty_queue
        }
        overwrite_data = json.dumps(overwrite_data, indent=4, ensure_ascii=False)
        with open("rest.json", "w") as outfile:
            outfile.write(overwrite_data)
        print(free_of_duty)
    return 

rest_exemption(12)
