import csv

with open('uses_practice.csv') as fr, open('users_output.csv', 'w') as fw:
    reader = csv.reader(fr)
    writer = csv.writer(fw)
    for row in reader:
        output =  '    "' + row[0] + '",'
        # print(output)
        writer.writerow([output)

