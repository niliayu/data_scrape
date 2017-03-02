# Post-process building data. String comparisons are modeled from Olin data string names.

import sys
import csv


# Process each file one at a time; append to one output file
def main(data_file):
    with open(data_file, 'r') as file:
        reader = csv.DictReader(file)
        print(reader)


# Can pass multiple files to script
if __name__ == "__main__":
   for file in sys.argv:
       if '.py' in file:
           pass # skip first argument
       else:
        main(file)

