import os
import sys
import pandas as pd
import numpy as np


def main():

    data_dir = "aois/aoi_part1_words/"
    text_trials_df = pd.read_csv("/Users/tzp466/Documents/code/copco-processing/aois/InterestAreas/RESULTS_FILE_part1_words.txt", delimiter="\t")
    for item in os.listdir(data_dir):
        if item.endswith('ias'):
            trial_no = item.split("_")[1].replace(".ias", "")
            m = text_trials_df.loc[text_trials_df["Trial_Index_"] == int(trial_no)]
            print(m["Trial_Index_"].values[0])
            #print(trial_no, m["Trial_Index_"], m.speechid, m.paragraphid)
            print('cp ' + data_dir+str(item) + ' new_aois/part1_IA_'+str(m.speechid.values[0]).strip()+'_'+str(m.paragraphid.values[0]).strip()+'_words.ias')
            os.system('cp ' + data_dir+str(item) + ' aois/new_aois/part1_IA_'+str(m.speechid.values[0]).strip()+'_'+str(m.paragraphid.values[0]).strip()+'_words.ias')


if __name__ == '__main__':
    main()
