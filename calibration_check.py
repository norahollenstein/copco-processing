import os
import sys
import pandas as pd
import numpy as np

# A really rough calibration checker
# Checks the calibration results of each participant from the .EDF files based on simple pattern matching
# usage: python calibration_check.py RawData/

# uncomment print lines below for details on calibration accuracy

def check_calibration():

    data_dir = "RawData/"
    subject_calibration_dict = {}
    for item in os.listdir(data_dir):
        if "P" in item:
            speeches_read = []
            subject_id = item
            edf_file_path = os.path.join(data_dir, item, subject_id+'.edf')
            #print(edf_file_path)

            with open(edf_file_path, mode='r', encoding='mac_roman') as file:

                edf_lines = file.readlines()
                blocks = 0

                subject_calibration_dict[subject_id] = []
                for line in edf_lines:
                    if "CAL VALIDATION HV9 " in line:
                        cal_line_idx = line.find("CAL VALIDATION HV9 ")
                        validation_outcome = line[cal_line_idx:cal_line_idx+90]
                        results = validation_outcome.split(" ")
                        eye = results[4]
                        grade = results[5]
                        avg_error = results[7]
                        max_error = results[9]
                        end_of_validation = line
                        #print(end_of_validation)
                        if "EXPERIMENT_CONTINUE" in end_of_validation:
                            if "GOOD" in validation_outcome:
                                #print(eye, grade, avg_error, max_error)
                                #print("GOOD calibration - experiment continued!")
                                blocks += 1
                                outcome = "GOOD"
                            elif "FAIR" in validation_outcome:
                                #print(eye, grade, avg_error, max_error)
                                #print("FAIR calibration - experiment continued!")
                                blocks += 1
                                outcome = 'FAIR'
                            elif "POOR" in validation_outcome:
                                #print(eye, grade, avg_error, max_error)
                                #print("WARNING!!! POOR calibration - experiment continued anyway!!!")
                                #print("CHECK experiment protocol!")
                                blocks += 1
                                outcome = "POOR"
                            subject_calibration_dict[subject_id].append(outcome)
                if not subject_calibration_dict[subject_id]:
                    print(subject_id, "No EXPERIMENT_CONTINUE flag found." )
    print("----")
    for x, y in subject_calibration_dict.items():
        print(x,y)

    return subject_calibration_dict

def main():
    check_calibration()

if __name__ == '__main__':
    main()
