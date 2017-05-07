# Created to test webpage scraping of Olin/White data

from datetime import datetime
import os
import csv
import requests
import re
import collections
import time
import sys

key = ''
row_entry = collections.OrderedDict()
query_url = ['http://129.22.155.18/status?title=&timeFormat=use24Hour&stationName=Case_Olin&swid=*&description'
             '=*&type1=AI&comparison1=%3D%3D&comparisonValue1=*&type2=BI&comparison2=%3D%3D&comparisonValue2=*&sort'
             '=swid&content-type=text%2Fcomma-separated-values',
             'http://129.22.155.18/status?title=&timeFormat=use24Hour&stationName=Case_White&swid=*&description'
             '=*&type1=AI&comparison1=%3D%3D&comparisonValue1=*&type2=BI&comparison2=%3D%3D&comparisonValue2=*&sort'
             '=swid&content-type=text%2Fcomma-separated-values']
buf = [] # empty list, will populate with list of dict entries needing to be added
timestr = {} # empty var to hold string of date/time info for buffer


def gen_dict_entry(path, data):
    split_path = path.split('/')

    if len(split_path[len(split_path)-1]) > 0:
        name = split_path[len(split_path)-1]
    else:
        name = split_path[len(split_path)-2] + split_path[len(split_path)-1]

    if ('Trends' not in path) and ((('schedule' not in path) or ('ac1_sch' in path)) and ("Rm413" not in path)):
        row_entry[col_title_checker(split_path, name)] = data_gen(data)


def col_title_checker(split, name):
    for frag in split:
        if 'Rm' in frag:
            return frag + '_' + name
    return name


def data_gen(data):  # strip units
    sub = re.sub('%', '', data)
    sub = sub.split(' ')[0]
    return sub


def csv_write(dict, filename):

    # create file if needed
    try:
        file = open(filename, 'r')
    except:
        file = open(filename, 'w+')
    file.close()

    header = header_sniffer(filename)

    try:
        with open(filename, 'a+') as file:

            data_writer = csv.DictWriter(file, dict.keys(), delimiter=',', lineterminator='\n')

            if not header:
                data_writer.writeheader()

            try:
                tmp = open('tmp.csv', 'r')
                tmp_reader = csv.DictReader(tmp)
                tmp_writer = csv.DictWriter(file, dict.keys(), delimiter=',', lineterminator='\n')
                for row in tmp_reader:
                    tmp_writer.writerow(row)

                try:
                    tmp.close()
                    os.remove(os.getcwd() + '\\tmp.csv')
                except:
                    print("Could not delete tmp.csv.")
            except:
                data_writer.writerow(dict)
    except PermissionError:
        header = header_sniffer('tmp.csv')
        file = open('tmp.csv', 'a+')
        data_writer = csv.DictWriter(file, dict.keys(), delimiter=',', lineterminator='\n')
        if not header:
            data_writer.writeheader()
        data_writer.writerow(dict)
        file.close()


def header_sniffer(filename):
    try:
        file = open(filename, 'r')
        return csv.Sniffer().has_header(file.readline())
    except:
        return False


def query(url, starttime):
    timestr['currtime'] = datetime.now()
    print(timestr.get('currtime'))
    starttime = check_time_delta(starttime, datetime.now())
    user, ps = get_creds()

    attempts = 1
    while attempts > 0:
        try:
            olin_pg = requests.get(url, auth=(user, ps))
            decode = olin_pg.content.decode('ISO-8859-1')
            olin_data = csv.reader(decode.splitlines(), delimiter=',')

            row_entry['Time'] = timestr.get('currtime')
            row_entry['Time Delta'] = timestr.get('delta')

            for row in olin_data:
                gen_dict_entry(row[0], row[3])

            attempts = -1
        except:
            attempts += 1

        if attempts > 10000:
            print("Tried 10000 attempts!")
            return -1

    return starttime


def check_time_delta(starttime, currtime):
    timestr['delta'] = (currtime - starttime).total_seconds()
    print(timestr.get('delta'))
    delta = (currtime - starttime).days
    if delta > 6:
        return datetime.now()  # 1 week has passed, create new file
    else:
        return starttime


def to_string(data):
    return "%s" % data


def get_creds():
    with open('user.txt', 'r') as file:
        cred = file.readline()
        split = cred.split(' ')
    return split[0], split[1]


def check_start(filename):
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            first_entry = next(reader)
            starttime = datetime.strptime(first_entry['Time'], '%Y-%m-%d %H:%M:%S.%f')
            timestr['delta'] = (datetime.now() - starttime).total_seconds()
            row_entry['Time Delta'] = timestr.get('delta')
    except:
        pass

def main(bldg, rate):

    starttime = datetime.now()
    rate = int(rate)

    if bldg.lower() == 'olin':
        url = query_url[0]
    elif bldg.lower() == 'white':
        url = query_url[1]
    else:
        print("Invalid building selection, must choose 'olin' or 'white'")
        return -1

    while True:
        starttime = query(url, starttime)
        filename = str(starttime.year) + '_' + str(starttime.month) + '_' + str(starttime.day) + '_' + bldg.lower() + '.csv'
        check_start(filename)
        csv_write(row_entry, filename)
        time.sleep(rate)  # sleep for rate seconds


if __name__ == "__main__":
   main(sys.argv[1], sys.argv[2])
