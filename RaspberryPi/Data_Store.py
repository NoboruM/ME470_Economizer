import csv
import numpy as np
def read_csv_and_write_to_new_file(input_file, output_file):
    # Open the input CSV file for reading
    with open(input_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        # Open the output file for writing
        with open(output_file, 'w', newline='') as new_file:
            csv_writer = csv.writer(new_file)
            
            # Read each row from the input CSV file and write to the new file
            for row in csv_reader:
                csv_writer.writerow(row)

# Example usage:
input_filename = 'test.csv'
output_filename = input("Enter the name for the output file (include .csv extension): ")
# keep arrays less than 60000000

read_csv_and_write_to_new_file(input_filename, output_filename)
