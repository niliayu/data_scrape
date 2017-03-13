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
            avg_sum(row, avg_temps_floor, avg_temps_exp, sum_boxflows_floor, sum_boxflows_exp)

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
            elif flowset == minflow:
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


def avg_sum(row, avg_output_floor, avg_output_exp, sum_output_floor, sum_output_exp):
    avg_exp = {}
    avg_floor = {}
    sum_exp = {}
    sum_floor = {}

    # empty dicts for ALL THE EXPOSURES
    north_temp = []
    south_temp = []
    east_temp = []
    west_temp = []
    
    north_flow = []
    south_flow = []
    east_flow = []
    west_flow = []

    # Empty dicts for ALL THE FLOORS
    floor2_temp = []
    floor3_temp = []
    floor4_temp = []
    floor5_temp = []
    floor6_temp = []
    floor7_temp = []
    floor8_temp = []

    floor2_flow = []
    floor3_flow = []
    floor4_flow = []
    floor5_flow = []
    floor6_flow = []
    floor7_flow = []
    floor8_flow = []

    for entry in row.keys():
        if ('Rm2' or 'RmF2') in entry:
            if 'temp' in entry.lower():
                floor2_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                floor2_flow.append(float(row[entry]))
        elif ('Rm3' or 'RmF3') in entry:
            if 'temp' in entry.lower():
                floor3_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                floor3_flow.append(float(row[entry]))
        elif ('Rm4' or 'RmF4') in entry:
            if 'temp' in entry.lower():
                floor4_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                floor4_flow.append(float(row[entry]))
        elif ('Rm5' or 'RmF5') in entry:
            if 'temp' in entry.lower():
                floor5_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                floor5_flow.append(float(row[entry]))
        elif ('Rm6' or 'RmF6') in entry:
            if 'temp' in entry.lower():
                floor6_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                floor6_flow.append(float(row[entry]))
        elif ('Rm7' or 'RmF7') in entry:
            if 'temp' in entry.lower():
                floor7_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                floor7_flow.append(float(row[entry]))
        elif ('Rm8' or 'RmF8') in entry:
            if 'temp' in entry.lower():
                floor8_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                floor8_flow.append(float(row[entry]))

        if 'NTH' in entry.upper():
            if 'temp' in entry.lower():
                north_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                north_flow.append(float(row[entry]))
        elif 'STH' in entry.upper():
            if 'temp' in entry.lower():
                south_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                south_flow.append(float(row[entry]))
        elif 'EST' in entry.upper():
            if 'temp' in entry.lower():
                east_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                east_flow.append(float(row[entry]))
        elif 'WST' in entry.upper():
            if 'temp' in entry.lower():
                west_temp.append(float(row[entry]))
            if 'boxflow' in entry.lower():
                west_flow.append(float(row[entry]))

    if(len(floor2_temp) > 0):
        avg_floor['floor2_avg_temp'] = sum_list(floor2_temp) / len(floor2_temp)
    else:
        avg_floor['floor2_avg_temp'] = 0
    sum_floor['floor2_sum_flows'] = sum_list(floor2_flow)

    if(len(north_temp) > 0):
        avg_exp['north_avg_temps'] = sum_list(north_temp) / len(north_temp)
    else:
        avg_exp['north_avg_temps'] = 0
    sum_exp['north_sum_flows'] = sum_list(north_flow)

    if(len(floor3_temp) > 0):
        avg_floor['floor3_avg_temp'] = sum_list(floor3_temp) / len(floor3_temp)
    else:
        avg_floor['floor3_avg_temp'] = 0
    sum_floor['floor3_sum_flows'] = sum_list(floor3_flow)

    if(len(south_temp) > 0):
        avg_exp['south_avg_temps'] = sum_list(south_temp) / len(south_temp)
    else:
        avg_exp['south_avg_temps'] = 0
    sum_exp['south_sum_flows'] = sum_list(south_flow)

    if(len(floor4_temp) > 0):
        avg_floor['floor4_avg_temp'] = sum_list(floor4_temp) / len(floor4_temp)
    else:
        avg_floor['floor4_avg_temp'] = 0
    sum_floor['floor4_sum_flows'] = sum_list(floor4_flow)

    if(len(east_temp) > 0):
        avg_exp['east_avg_temps'] = sum_list(east_temp) / len(east_temp)
    else:
        avg_exp['east_avg_temps'] = 0
    sum_exp['east_sum_flows'] = sum_list(east_flow)

    if(len(floor5_temp) > 0):
        avg_floor['floor5_avg_temp'] = sum_list(floor5_temp) / len(floor5_temp)
    else:
        avg_floor['floor5_avg_temp'] = 0
    sum_floor['floor5_sum_flows'] = sum_list(floor5_flow)

    if(len(west_temp) > 0):
        avg_exp['west_avg_temps'] = sum_list(west_temp) / len(west_temp)
    else:
        avg_exp['west_avg_temps'] = 0
    sum_exp['west_sum_flows'] = sum_list(west_flow)

    if(len(floor6_temp) > 0):
        avg_floor['floor6_avg_temp'] = sum_list(floor6_temp) / len(floor6_temp)
    else:
        avg_floor['floor6_avg_temp'] = 0
    sum_floor['floor6_sum_flows'] = sum_list(floor6_flow)

    if(len(floor7_temp) > 0):
        avg_floor['floor7_avg_temp'] = sum_list(floor7_temp) / len(floor7_temp)
    else:
        avg_floor['floor7_avg_temp'] = 0
    sum_floor['floor7_sum_flows'] = sum_list(floor7_flow)

    if(len(floor8_temp) > 0):
        avg_floor['floor8_avg_temp'] = sum_list(floor7_temp) / len(floor7_temp)
    else:
        avg_floor['floor8_avg_temp'] = 0
    sum_floor['floor8_sum_flows'] = sum_list(floor7_flow)

    avg_output_floor.append(avg_floor)
    avg_output_exp.append(avg_exp)
    sum_output_floor.append(sum_floor)
    sum_output_exp.append(sum_exp)


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
