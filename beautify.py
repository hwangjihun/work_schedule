import json
import csv
#THings to fix (somehow 2 탕 IS GOING STRAIGHT ON consecutively)
time_dict = {
    1: '08:00 ~ 10:00',
    2: '10:00 ~ 12:00',
    3: '12:00 ~ 14:00',
    4: '14:00 ~ 16:00',
    5: '16:00 ~ 18:00',
    6: '18:00 ~ 20:00',
    7: '20:00 ~ 22:00',
    8: '22:00 ~ 00:00',
    9: '00:00 ~ 02:00',
    10: '02:00 ~ 04:00',
    11: '04:00 ~ 06:00',
    12: '06:00 ~ 08:00'
}

with open('./archive/json/2023-12-20.json') as json_file:
    data = json.load(json_file)
    print(data)
workers_data = data['members']
 
data_file = open('./archive/csv/2023-12-20.csv', 'w')
csv_writer = csv.writer(data_file)
 
# Counter variable used for writing 
# headers to the CSV file
count = 0
 
for worker in workers_data:
    if count == 0:
        # Writing headers of CSV file
        header = list(worker.keys())
        csv_writer.writerow([header[1], header[0]])
        count += 1
 
    # Writing data of CSV file
    updated_worker = list(worker.values())

    csv_writer.writerow([time_dict[updated_worker[1]], updated_worker[0]])
 
data_file.close()