# Post-process building data. String comparisons are modeled from Olin data string names.

import sys
import csv


floor = [0] * 9
exposure = [0] * 5
avg_temps = [0] * len(floor)
sum_boxflows = [0] * len(floor)


# Process each file one at a time; append to one output file
def main(data_file):
    with open(data_file, 'r') as file:
        reader = csv.DictReader(file)

        # generate floors
        for row in reader:
            floor_data(row)

    temp_avg()
    print(avg_temps)

    sum_flows()
    print(sum_boxflows)


def temp_avg():
    # generate temperature avgs for each floor
    for entry in range(1, len(floor)):
        tmp_list = []
        try:
            for keys in floor[entry].keys():
                if ('temp' or 'Temp') in keys:
                    tmp_list.append(float(floor[entry][keys]))
            avg_temps[entry] = sum(tmp_list) / len(tmp_list)
        except:
            pass


def sum_flows():
    # sum bloxflows for each floor
    for entry in range(1, len(floor)):
        tmp_list = []
        try:
            for keys in floor[entry].keys():
                if 'boxflow' in keys:
                    tmp_list.append(float(floor[entry][keys]))
            sum_boxflows[entry] = sum(tmp_list)
        except:
            pass


def floor_data(row):

    # Empty dicts for ALL THE FLOORS
    floor2 = {}
    floor3 = {}
    floor4 = {}
    floor5 = {}
    floor6 = {}
    floor7 = {}
    floor8 = {}

    for entry in row.keys():
        for floor_num in range(2, 8): # TODO: check if this is inclusive or exclusive?
            if ('Rm2' or 'RmF2') in entry:
                floor2[entry] = row[entry]
                floor[2] = floor2
            elif ('Rm3' or 'RmF3') in entry:
                floor3[entry] = row[entry]
                floor[3] = floor3
            elif ('Rm4' or 'RmF4') in entry:
                floor4[entry] = row[entry]
                floor[4] = floor4
            elif ('Rm5' or 'RmF5') in entry:
                floor5[entry] = row[entry]
                floor[5] = floor5 
            elif ('Rm6' or 'RmF6') in entry:
                floor6[entry] = row[entry]
                floor[6] = floor6  
            elif ('Rm7' or 'RmF7') in entry:
                floor7[entry] = row[entry]
                floor[7] = floor7 
            elif ('Rm8' or 'RmF8') in entry:
                floor8[entry] = row[entry]
                floor[8] = floor8


# def exp_data(row):
#


def sum(list):
    sum = 0
    for x in list:
        sum += x
    return sum


# Can pass multiple files to script
if __name__ == "__main__":
   for file in sys.argv:
       if '.py' in file:
           pass # skip first argument
       else:
        main(file)

