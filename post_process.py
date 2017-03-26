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

    # clear arrays for new file
    avg_temps_floor.clear()
    sum_boxflows_floor.clear()
    avg_temps_exp.clear()
    sum_boxflows_exp.clear()
    max_min.clear()
    flow_error.clear()
    temp_error.clear()

    with open(data_file, 'r') as file:
        reader = csv.DictReader(file)

        print("Processing %s..." % str(data_file))

        # generate floors
        count = 0
        for row in reader:
            floor_data(row, floor_)
            exp_data(row, exposure)
            flow_error_check(row, max_min, flow_error)
            temp_error_check(row, temp_error)
            process_floor(row, avg_temps_floor, sum_boxflows_floor)
            process_exposure(row, avg_temps_exp, sum_boxflows_exp)
            count += 1

    print("Processed %d rows." % count)
    print("Writing to file...")
    write_csv(file, max_min, 'max_min_')
    write_csv(file, flow_error, 'flow_error_')
    write_csv(file, temp_error, 'temp_error_')

    write_csv(file, avg_temps_exp, 'avg_temps_exp_')
    write_csv(file, avg_temps_floor, 'avg_temps_floor_')
    write_csv(file, sum_boxflows_exp, 'sum_boxflows_exp_')
    write_csv(file, sum_boxflows_floor, 'sum_boxflows_floor_')

    print("Done.")


def write_csv(datafile, list, name):
    filename = name + datafile.name
    with open(filename, 'w+') as file:
        first = list.pop()
        writer = csv.DictWriter(file, first.keys(), delimiter=',', lineterminator='\n')
        writer.writeheader()
        writer.writerow(first)
        for entry in list:
            writer = csv.DictWriter(file, entry.keys(), delimiter=',', lineterminator='\n')
            writer.writerow(entry)


def temp_error_check(row, output):
    tmp = {}
    for entry in row.keys():
        if 'spacesetpoint' in entry:
            add_time(row, tmp)
            tmp[entry] = float(row[entry]) - float(row[entry.replace('spacesetpoint', 'spacetemp')])
    output.append(tmp)


def flow_error_check(row, max_min_check, error_check):
    tmp_mm = {}
    tmp_err = {}

    bldg_min = 0
    bldg_max = 0
    bldg_flo = 0
    bldg_tot = 0

    for entry in row.keys():
        if 'flowsetpoint' in entry.lower():

            add_time(row, tmp_err)
            add_time(row, tmp_mm)

            flowset = float(row[entry])
            flow = float(row[entry.replace('flowsetpoint', 'boxflow')])
            maxflow = float(row[entry.replace('flowsetpoint', 'maxflow')])
            minflow = float(row[entry.replace('flowsetpoint', 'minflow')])

            bldg_flo += flow
            bldg_tot += maxflow

            if flowset == maxflow:
                tmp_mm[entry] = 100  # max flow
                bldg_max += 1
            elif (flowset == minflow) or (maxflow == 0):
                tmp_mm[entry] = 0
                bldg_min += 1
            else:
                tmp_mm[entry] = ((maxflow - flow)/maxflow)*100

            try:
                tmp_err[entry] = ((flowset - flow)/flowset)*100
            except:  # div by 0
                try:
                    tmp_err[entry] = ((flowset - flow) / (flowset + flow)) * 100
                except:  # still div by 0!?
                    tmp_err[entry] = 0

    try:
        tmp_mm["% at max"] = bldg_max/len(tmp_err)
    except:
        tmp_mm["% at max"] = 0

    try:
        tmp_mm["% at min"] = bldg_min/len(tmp_err)
    except:
        tmp_mm["% at min"] = 0

    try:
        tmp_mm["% overall"] = bldg_flo/bldg_tot
    except ZeroDivisionError:
        tmp_mm["% overall"] = 0

    max_min_check.append(tmp_mm)
    error_check.append(tmp_err)


def add_time(row, output):
    try:
        output.append(row['Time'])
        output.append(row['Time Delta'])  # Add some error checking here
    except:
        output['Time'] = row['Time']
        output['Time Delta'] = row['Time Delta']


def process_exposure(row, avg_output_exp, sum_output_exp):
    # right now assume exposures will be found in exposures.csv in this directory
    exp = {}
    with open('exposures.csv', 'r') as file:
        reader = csv.reader(file)
        for row_ in reader:
            exp[row_[0]] = row_[1] # Rm : n/s/e/w

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
                if ('temp' in entry) or ('temp' in entry and 'rmf' in entry.lower() and 'b' in exp_l):
                    temp_dict[exp_l + '_temp'].append(float(row[entry]))
                if 'boxflow' in entry:
                    flow_dict[exp_l + '_flow'].append(float(row[entry]))

    for entry in temp_dict:
        try:
            avg_exp[entry] = sum_list(temp_dict[entry])/len(temp_dict[entry])
        except ZeroDivisionError:
            avg_exp[entry] = 0

    for entry in flow_dict:
        sum_exp[entry] = sum_list(flow_dict[entry])

    avg_output_exp.append(avg_exp)
    sum_output_exp.append(sum_exp)


def process_floor(row, avg_output_floor, sum_output_floor):
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
        for level in range(2,9):
            floor = 'floor' + str(level)
            if ('rm' + str(level)) in entry.lower():
                if 'temp' in entry.lower():
                    temp_dict[floor + '_temp'].append(float(row[entry]))
            if (('rm' + str(level)) in entry.lower()) or (('rmf' + str(level)) in entry.lower()):
                if 'boxflow' in entry.lower():
                    flow_dict[floor + '_flow'].append(float(row[entry]))

    for entry in temp_dict:
        try:
            avg_floor[entry] = sum_list(temp_dict[entry])/len(temp_dict[entry])
        except ZeroDivisionError:
            avg_floor[entry] = 0

    for entry in flow_dict:
        sum_floor[entry] = sum_list(flow_dict[entry])

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


# Can pass multiple files to script
if __name__ == "__main__":
   for file in sys.argv:
       if '.py' in file:
           pass # skip first argument
       else:
        main(file)