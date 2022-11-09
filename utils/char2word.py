import os
import pandas as pd
from ast import literal_eval
import numpy as np

# read interest area reports and convert character-level fixation into word-level gaze features

def get_part(speechid):
    experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946, 22811, 26682, 202150, 202151, 202152, 202204, 202205, 202206], "2": [1317, 1125, 7856, 10365, 1323, 7797, 1165, 1318, 10440, 17526, 202201, 202202, 202203, 202207, 202208, 202209]}
    for k,v in experiment_parts.items():
        if speechid in v:
            part = k
    return part

report_dir = "InterestAreaReports/"
for file in os.listdir(report_dir):
    if file.endswith("-utf8.txt"):
        print(file)
        data = pd.read_csv(report_dir+file, delimiter="\t", converters={"INTEREST_AREA_FIXATION_SEQUENCE": literal_eval})
        trials = data.groupby(["TRIAL_INDEX"])
        subject = data['RECORDING_SESSION_LABEL'].unique()[0]
        print(subject)
        word_df = pd.DataFrame(columns=['trialId','speechId', 'paragraphId', 'wordId', 'word', 'word_fixated', 'number_of_fixations', 'word_landing_position_char', 'word_landing_position_index', 'word_first_fixation_duration', 'word_mean_fixation_duration', 'word_first_char_dwell_time', 'word_total_fix_time', 'word_gaze_duration', 'word_go_past_time'])
        for trial_no, trial_data in trials:
            char_map = {}
            word_map = {}
            word2char = {}
            for cidx, c in enumerate(trial_data["IA_LABEL"].values):
                char_map[cidx+1] = c
            #print("trial:", trial_no, trial_data.speechid.values[0], trial_data.paragraphid.values[0])
            part = get_part(trial_data['speechid'].unique()[0])
            word_ias = pd.read_csv('aois/new_aois/part'+part+'_IA_'+str(trial_data.speechid.values[0]).strip()+'_'+str(trial_data.paragraphid.values[0]).strip()+'_words.ias', delimiter="\t", header=None)
            trial_char_ind = 1
            for widx, word in enumerate(word_ias[6].values):
                word_map[widx+1] = word
                word2char[widx+1] = []
                for c in word:
                    if char_map[trial_char_ind] == c:
                        word2char[widx+1].append(trial_char_ind)
                    trial_char_ind += 1
            #print(word_map)
            #print(word2char)
            trial_fix_outside_ias = list(trial_data['INTEREST_AREA_FIXATION_SEQUENCE'].values[0]).count(0)
            #print("trial_fix_outside_ias:", trial_fix_outside_ias)

            trial_fixation_nos = 0

            for w, chars in word2char.items():

                word_chars = [char_map[c] for c in chars]

                word_fix_sequence = [i for i in list(trial_data['INTEREST_AREA_FIXATION_SEQUENCE'].values[0]) if i in chars]
                number_of_fixations = len(word_fix_sequence)
                trial_fixation_nos += number_of_fixations

                if word_fix_sequence:
                    word_fixated = True

                    word_first_fixation_id = word_fix_sequence[0]
                    first_char = trial_data.loc[trial_data['IA_ID'] == word_first_fixation_id]
                    all_chars = trial_data.loc[trial_data['IA_ID'].isin(word_fix_sequence)]
                    word_first_fixation_duration = int(first_char['IA_FIRST_FIXATION_DURATION'].values[0])
                    # todo: do we need this next one?
                    word_first_char_dwell_time = int(first_char['IA_DWELL_TIME'].values[0])
                    word_total_fix_time = all_chars['IA_DWELL_TIME'].sum()
                    # word landing position: specific character and index of char within word
                    word_landing_position_char = first_char['IA_LABEL'].values[0]
                    word_char_ids = list(trial_data.loc[trial_data['IA_ID'].isin(chars),'IA_ID'])
                    word_landing_position_index = word_char_ids.index(first_char['IA_ID'].values[0])
                    word_mean_fixation_duration = word_total_fix_time / number_of_fixations

                    # todo: based on IA_FIRST_FIXATION_PREVIOUS_IAREAS	IA_FIRST_FIXATION_RUN_INDEX	or IA_FIRST_FIX_PROGRESSIVE, find out if there were regression to previous words or regressions from latter words to current word

                    word_gaze_duration = word_total_fix_time
                    word_go_past_time = word_total_fix_time

                    trial_fix_sequence = list(trial_data['INTEREST_AREA_FIXATION_SEQUENCE'].values[0])
                    for fixid, fix in enumerate(word_fix_sequence):
                        this_fix_seq_idx = [i for i, e in enumerate(trial_fix_sequence) if e == fix][0]
                        # todo: what to do if there are multiple? nothing because we take dwell time?

                        word_gaze_duration = all_chars[all_chars['IA_ID'] == fix]['IA_DWELL_TIME'].values[0]
                        word_go_past_time = all_chars[all_chars['IA_ID'] == fix]['IA_DWELL_TIME'].values[0]
                        #print(word_gaze_duration, word_go_past_time)
                        try:
                            next_fix_seq_idx = [i for i, ia in enumerate(trial_fix_sequence) if ia == word_fix_sequence[fixid+1]][0]

                            if next_fix_seq_idx != this_fix_seq_idx+1:
                                if next_fix_seq_idx < this_fix_seq_idx:
                                    word_gaze_duration -= trial_data[trial_data['IA_ID'] == word_fix_sequence[fixid+1]]['IA_DWELL_TIME'].values[0]

                        except IndexError:
                            # last fixation
                            continue

                else:
                    word_fixated = False
                    word_landing_position_char = 'NA'
                    word_landing_position_index = 'NA'
                    word_first_fixation_duration = 'NA'
                    word_mean_fixation_duration = 'NA'
                    word_first_char_dwell_time = 'NA'
                    word_total_fix_time = 'NA'
                    word_gaze_duration = 'NA'
                    word_go_past_time = 'NA'

                word_data = [[trial_no, trial_data.speechid.values[0], trial_data.paragraphid.values[0], w, word_map[w], word_fixated, number_of_fixations, word_landing_position_char, word_landing_position_index, word_first_fixation_duration, word_mean_fixation_duration, word_first_char_dwell_time, word_total_fix_time, word_gaze_duration, word_go_past_time]]
                word_data_df = pd.DataFrame(word_data, columns=['trialId','speechId', 'paragraphId', 'wordId', 'word', 'word_fixated', 'number_of_fixations', 'word_landing_position_char', 'word_landing_position_index', 'word_first_fixation_duration', 'word_mean_fixation_duration', 'word_first_char_dwell_time', 'word_total_fix_time', 'word_gaze_duration', 'word_go_past_time'])
                #word_df.append(word_data_df)
                word_df = pd.concat([word_df, word_data_df])

            # TODO: use TRIAL_FIXATION_COUNT to check if it is equal to the sum of number_of_fixations in trial
            # this is always less - check why
            #if trial_fixation_nos <= trial_data['TRIAL_FIXATION_COUNT'].values[0]:
                #print(trial_data['TRIAL_FIXATION_COUNT'].values[0]-trial_fixation_nos, " fixations outside of character interest areas")
            #else:
                # sanitiy check
            #    print("WARNING: too many fixations detected!")

        word_df.to_csv("word_feature_reports/"+subject+"_word_features.csv", index=False, encoding='utf-8')
