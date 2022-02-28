import os
import pandas as pd
from ast import literal_eval
import numpy as np


# character mapping to correct mistakes



# read interest area reports and convert character-level fixation into word-level gaze features
def get_part(speechid):
    #print(speechid)
    experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946, 22811, 26682], "2": [1317, 1125, 7856, 10365, 1323, 7797, 1165, 1318, 10440, 17526]}
    for k,v in experiment_parts.items():
        if speechid in v:
            part = k
    return part

part = "2"
report_dir = "aois/aoi_part"+part+"_chars/"

char_areas_df = pd.DataFrame(columns=['part', 'trialId', 'charId', 'l', 'b', 'r', 't', 'char'])

for file in os.listdir(report_dir):
    if file.endswith(".ias"):
        print(file)
        trial = file.split("_")[1].replace(".ias", "")
        #print(trial)
        data = pd.read_csv(report_dir+file, delimiter="\t", header=None)
        #print(data)
        for idx, row in data.iterrows():
            char_info = [[part, trial, row[1], row[2], row[3], row[4], row[5], row[6]]]
            df = pd.DataFrame(char_info, columns=['part', 'trialId', 'charId', 'l', 'b', 'r', 't', 'char'])
            char_areas_df = pd.concat([char_areas_df, df])
print(len(char_areas_df))
char_areas_df.to_csv("part"+part+"_char_areas.csv")
