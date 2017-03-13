# Post-process building data. String comparisons are modeled from Olin data string names.

import csv
import sys

floor = [0] * 9
exposure = [0] * 5
avg_temps_floor = []
sum_boxflows_floor = []
avg_temps_exp = []
sum_boxflows_exp = []
max_min = []
flow_error = []
temp_error = []


# Process each file one at a time; append to one output file
def main(data_file):
    with open(data_file, 'r') as file:
        reader = csv.DictReader(file)

        # generate floors
        for row in reader:
            floor_data(row, floor)
            exp_data(row, exposure)
            flow_error_check(row, max_min, flow_error)
            temp_error_check(row, temp_error)

    floor_headers = ['floor0', 'floor1', 'floor2', 'floor3', 'floor4', 'floor5', 'floor6', 'floor7', 'floor8']
    exposure_headers = ['NTH', 'STH', 'EST', 'WST']

    temp_avg(floor, floor_headers, avg_temps_floor)
    temp_avg(exposure, exposure_headers, avg_temps_exp)

    sum_flows(floor, floor_headers, sum_boxflows_floor)
    sum_flows(exposure,  exposure_headers, sum_boxflows_exp)

    write_csv(file, max_min, 'max_min_')
    write_csv(file, flow_error, 'flow_error_')
    write_csv(file, temp_error, 'temp_error_')

    write_csv(file, avg_temps_exp, 'avg_temps_exp_')
    write_csv(file, avg_temps_floor, 'avg_temps_floor_')
    write_csv(file, sum_boxflows_exp, 'sum_boxflows_exp_')
    write_csv(file, sum_boxflows_floor, 'sum_boxflows_floor_')


def write_csv(datafile, list, name):
    filename = name + datafile.name
    with open(filename, 'w+') as file:
        first = list.pop()
        writer = csv.DictWriter(file, first.keys(), delimiter=',', lineterminator='\n')
        writer.writeheader()
        writer.writerow(first)
        for entry in list:
            # blank = csv.writer(file)
            # blank.writerow("\n")
            writer = csv.DictWriter(file, entry.keys(), delimiter=',', lineterminator='\n')
            # writer.writeheader()
            writer.writerow(entry)


def temp_error_check(row, output):
    tmp = {}
    for entry in row.keys():
        if 'spacesetpoint' in entry:
            add_time(row, tmp)
            tmp[entry] = abs(float(row[entry]) - float(row[entry.replace('spacesetpoint', 'spacetemp')]))
    output.append(tmp)


def flow_error_check(row, max_min_check, error_check):
    tmp_mm = {}
    tmp_err = {}
    for entry in row.keys():
        if 'flowsetpoint' in entry.lower():

            add_time(row, tmp_err)
            add_time(row, tmp_mm)

            flowset = float(row[entry])
            flow = float(row[entry.replace('flowsetpoint', 'boxflow')])
            maxflow = float(row[entry.replace('flowsetpoint', 'maxflow')])
            minflow = float(row[entry.replace('flowsetpoint', 'minflow')])
            if flowset == maxflow:
                tmp_mm[entry] = 'max'  # max flow
            elif flowset == minflow:
                tmp_mm[entry] = 'min'
            else:
                tmp_mm[entry] = str(abs((maxflow - flow)/maxflow)*100) + '%'

            try:
                tmp_err[entry] = abs((flowset - flow)/flowset)*100
            except:  # div by 0
                try:
                    tmp_err[entry] = abs((flowset - flow) / (flowset + flow)) * 100
                except:  # still div by 0!?
                    tmp_err[entry] = 0

    max_min_check.append(tmp_mm)
    error_check.append(tmp_err)


def add_time(row, output):
    try:
        output.append(row['Time'])
        output.append(row['Time Delta'])  # Add some error checking here
    except:
        output['Time'] = row['Time']
        output['Time Delta'] = row['Time Delta']


def temp_avg(list, headers, output):
    # generate temperature avgs for each floor
    tmp_dict = {}
    for entry in range(0, len(list)):
        tmp_list = []
        key = ''
        try:
            for keys in list[entry].keys():
                if ('temp' or 'Temp') in keys:
                    tmp_list.append(float(list[entry][keys]))
                for label in headers:
                    if label == find_est(keys):
                        key = label

            if len(key) < 1:
                key = headers[entry]

            try:
                tmp_dict[key] = sum_list(tmp_list) / len(tmp_list)
            except:
                tmp_dict[key] = 0
        except:
            pass
    output.append(tmp_dict)


def sum_flows(list, headers, output):
    # sum boxflows for each floor
    tmp_dict = {}
    for entry in range(0, len(list)):
        tmp_list = []
        key = ''
        try:
            for keys in list[entry].keys():
                if 'boxflow' in keys:
                    tmp_list.append(float(list[entry][keys]))
                for label in headers:
                    if label == find_est(keys):
                        key = label

            if len(key) > 0:
                tmp_dict[key] = sum_list(tmp_list)
            else:
                tmp_dict[headers[entry]] = sum_list(tmp_list)
        except:
            pass
    output.append(tmp_dict)

def floor_data(row, output):

    # Empty dicts for ALL THE FLOORS
    floor2 = {}
    floor3 = {}
    floor4 = {}
    floor5 = {}
    floor6 = {}
    floor7 = {}
    floor8 = {}

    for entry in row.keys():
        if ('Rm2' or 'RmF2') in entry:
            floor2[entry] = row[entry]
            output[2] = floor2
        elif ('Rm3' or 'RmF3') in entry:
            floor3[entry] = row[entry]
            output[3] = floor3
        elif ('Rm4' or 'RmF4') in entry:
            floor4[entry] = row[entry]
            output[4] = floor4
        elif ('Rm5' or 'RmF5') in entry:
            floor5[entry] = row[entry]
            output[5] = floor5
        elif ('Rm6' or 'RmF6') in entry:
            floor6[entry] = row[entry]
            output[6] = floor6
        elif ('Rm7' or 'RmF7') in entry:
            floor7[entry] = row[entry]
            output[7] = floor7
        elif ('Rm8' or 'RmF8') in entry:
            floor8[entry] = row[entry]
            output[8] = floor8


def exp_data(row, output):
    # empty dicts for ALL THE EXPOSURES
    north = {}
    south = {}
    east = {}
    west = {}

    for entry in row.keys():
        if 'NTH' in entry.upper():
            north[entry] = row[entry]
            output[0] = north
        elif 'STH' in entry.upper():
            south[entry] = row[entry]
            output[1] = south
        elif 'EST' in entry.upper():
            east[entry] = row[entry]
            output[2] = east
        elif 'WST' in entry.upper():
            west[entry] = row[entry]
            output[3] = west


def sum_list(list):
    sum = 0
    for x in list:
        sum += x
    return sum

def find_est(string):
    string = string.upper()
    if "NTH" in string:
        return "NTH"
    elif "STH" in string:
        return "STH"
    elif "EST" in string:
        return "EST"
    elif "WST" in string:
        return "WST"

# Can pass multiple files to script
if __name__ == "__main__":
   for file in sys.argv:
       if '.py' in file:
           pass # skip first argument
       else:
        main(file)

