# Post-process building data. String comparisons are modeled from Olin data string names.

import csv
import sys

floor_ = [0] * 9
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
            floor_data(row, floor_)
            exp_data(row, exposure)
            flow_error_check(row, max_min, flow_error)
            temp_error_check(row, temp_error)
            avg_sum_floor(row, avg_temps_floor, sum_boxflows_floor)
            avg_sum_exposure(row, avg_temps_exp, sum_boxflows_exp)

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
                tmp_mm[entry] = 100  # max flow
            elif (flowset == minflow) or (maxflow == 0):
                tmp_mm[entry] = 0
            else:
                tmp_mm[entry] = abs((maxflow - flow)/maxflow)*100

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


def avg_sum_exposure(row, avg_output_exp, sum_output_exp): # right now assume exposures will be found in exposures.csv in this directory
    # exp = {'n' : [], 's' : [], 'e' : [], 'w' : []}
    exp = {}
    with open('exposures.csv', 'r') as file:
        reader = csv.reader(file)
        for row_ in reader:
            exp[row_[0]] = row_[1] # Rm : n/s/e/w
            # for key in exp:
            #     if row[1] == key:
            #         exp[key] = row[0]

    avg_exp = {}
    sum_exp = {}

    temp_dict = {'n_temp' : [], 's_temp' : [], 'e_temp' : [], 'w_temp' : [], 'c_temp' : [], 'b_temp' : []}
    flow_dict = {'n_flow': [], 's_flow': [], 'e_flow': [], 'w_flow': [], 'c_flow' : [], 'b_flow' : []}

    add_time(row, avg_exp)
    add_time(row, sum_exp)

    for entry in row:
        for key in exp:
            if (key in entry) and (len(exp[key]) > 0):
                exp_l = str(exp[key])
                if 'temp' in entry:
                    temp_dict[exp_l + '_temp'].append(float(row[entry]))
                if 'boxflow' in entry:
                    flow_dict[exp_l + '_flow'].append(float(row[entry]))

    # TODO : processing, population of sums and averages


def avg_sum_floor(row, avg_output_floor, sum_output_floor):
    avg_floor = {}
    sum_floor = {}

    # Empty dicts for ALL THE FLOORS
    temp_dict = {'floor2_temp' : [], 'floor3_temp' : [], 'floor4_temp' : [], 'floor5_temp' : [], 'floor6_temp' : [],
                 'floor7_temp' : [], 'floor8_temp' : []}
    flow_dict = {'floor2_flow': [], 'floor3_flow': [], 'floor4_flow': [], 'floor5_flow': [], 'floor6_flow': [],
                 'floor7_flow': [], 'floor8_flow': []}

    add_time(row, avg_floor)
    add_time(row, sum_floor)

    for entry in row.keys():
        for level in range(2,8):
            if ('rm' + str(level)) in entry.lower():
                floor = 'floor' + str(level)
                if 'temp' in entry.lower():
                    temp_dict[floor + '_temp'].append(float(row[entry]))
                if 'boxflow' in entry.lower():
                    flow_dict[floor + '_flow'].append(float(row[entry]))


    level = 2
    for entry in temp_dict.values():
        floor = 'floor' + str(level)
        try:
            avg_floor[floor + '_avg_temp'] = sum_list(entry)/len(entry)
        except ZeroDivisionError:
            avg_floor[floor + '_avg_temp'] = 0
        level += 1

    level = 2
    for entry in flow_dict.values():
        floor = 'floor' + str(level)
        sum_floor[floor + '_sum_flows'] = sum_list(entry)
        level += 1

    avg_output_floor.append(avg_floor)
    sum_output_floor.append(sum_floor)


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
        try:
            sum += x
        except TypeError:
            pass
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