import os
import sys
import pandas as pd
import numpy as np


def main():

    data_dirs = ["aois_aug22/aois_part1_char/", "aois_aug22/aois_part2_word/", "aois_aug22/aois_part2_char/", "aois_aug22/aois_part1_word/"]
    for data_dir in data_dirs:
        part = data_dir[-7]
        type = data_dir[-5:-1]
        data_dir = data_dir+"aoi/"
        print(data_dir, type, part)
        text_trials_df = pd.read_csv("/Users/tzp466/Documents/code/copco-processing/aois/InterestAreas/RESULTS_FILE_part"+part+"_wiki_"+type+"s.txt", delimiter="\t")
        for item in os.listdir(data_dir):
            if item.endswith('ias'):
                trial_no = item.split("_")[1].replace(".ias", "")
                m = text_trials_df.loc[text_trials_df["Trial_Index_"] == int(trial_no)]
                #print(trial_no, m["Trial_Index_"].values[0], m.speechid, m.paragraphid)
                #print(m.speechid.values[0])
                print('cp ' + data_dir+str(item) + ' renamed_aois_aug22/part'+part+'_IA_'+str(m.speechid.values[0]).strip()+'_'+str(m.paragraphid.values[0]).strip()+'_'+type+'s.ias')
                os.system('cp ' + data_dir+str(item) + ' renamed_aois_aug22/part'+part+'_IA_'+str(m.speechid.values[0]).strip()+'_'+str(m.paragraphid.values[0]).strip()+'_'+type+'s.ias')
                print()
if __name__ == '__main__':
    main()
