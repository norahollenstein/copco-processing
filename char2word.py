import os
import pandas as pd
from ast import literal_eval

# read interest area reports and convert character-level fixation into word-level gaze features

def get_part(speechid):
    #print(speechid)
    experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946], "2": [1317, 1125, 7856, 10365, 1323, 7797,  1165,  1318, 10440, 17526]}
    for k,v in experiment_parts.items():
        if speechid in v:
            part = k
    return part

report_dir = "IA_Reports_utf8/"
for file in os.listdir(report_dir):
    print(file)
    data = pd.read_csv(report_dir+file, delimiter="\t", converters={"INTEREST_AREA_FIXATION_SEQUENCE": literal_eval})
    print(data['speechid'].unique())
    trials = data.groupby(["TRIAL_INDEX"])
    subject = data['RECORDING_SESSION_LABEL'].unique()[0]
    print(subject)
    word_df = pd.DataFrame(columns=['trialId', 'speechId', 'paragraphId', 'wordId', 'word', 'word_fixated', 'number_of_fixations', 'word_landing_position', 'word_first_fixation_duration', 'word_first_char_dwell', 'word_total_fix_time'])
    for trial_no, trial_data in trials:
        char_map = {}
        word_map = {}
        word2char = {}
        #print(trial_no, trial_data["IA_LABEL"].values)
        for cidx, c in enumerate(trial_data["IA_LABEL"].values):
            char_map[cidx+1] = c
        #print(char_map)
        #print("trial:", trial_no, trial_data.speechid.values[0], trial_data.paragraphid.values[0])
        part = get_part(trial_data['speechid'].unique()[0])
        word_ias = pd.read_csv('aois/new_aois/part'+part+'_IA_'+str(trial_data.speechid.values[0]).strip()+'_'+str(trial_data.paragraphid.values[0]).strip()+'_words.ias', delimiter="\t", header=None)
        print('aois/new_aois/part'+part+'_IA_'+str(trial_data.speechid.values[0]).strip()+'_'+str(trial_data.paragraphid.values[0]).strip()+'_words.ias')
        trial_char_ind = 1
        for widx, word in enumerate(word_ias[6].values):
            word_map[widx+1] = word
            word2char[widx+1] = []
            for c in word:
                #print(c, trial_char_ind)
                if char_map[trial_char_ind] == c:
                    word2char[widx+1].append(trial_char_ind)
                trial_char_ind += 1
        #print(word_map)

        #print(word2char)
        trial_fix_outside_ias = list(trial_data['INTEREST_AREA_FIXATION_SEQUENCE'].values[0]).count(0)
        #print("trial_fix_outside_ias:", trial_fix_outside_ias)

        for w, chars in word2char.items():
            #print(w, chars)
            #print(trial_data.loc[trial_data['IA_ID'].isin(chars)][['IA_LABEL', 'IA_ID']])

            word_fix_sequence = [i for i in list(trial_data['INTEREST_AREA_FIXATION_SEQUENCE'].values[0]) if i in chars]
            number_of_fixations = len(word_fix_sequence)

            if word_fix_sequence:
                word_fixated = True

                word_first_fixation_id = word_fix_sequence[0]
                first_char = trial_data.loc[trial_data['IA_ID'] == word_first_fixation_id]
                all_chars = trial_data.loc[trial_data['IA_ID'].isin(word_fix_sequence)]
                word_first_fixation_duration = int(first_char['IA_FIRST_FIXATION_DURATION'].values[0])
                word_first_char_dwell = int(first_char['IA_DWELL_TIME'].values[0])
                word_total_fix_time = all_chars['IA_DWELL_TIME'].sum()
                word_landing_position = first_char['IA_LABEL'].values[0]

                # TODO: define first run for full word: sum up to last letter IA with "first run"
                # first pass fixation time: FPFT
                # (GPT), the sum of all fixations prior to progressing to the right of the current word, including regressions to previous words that originated from the current word.
                # TFT: total fixation time: all fixations on this word
                # TRT: total reading time: the sum of all fixation durations on the current word, including regressions
                # new feature: fixation order: which word was fixated first

            else:
                word_fixated = False
                word_landing_position = ''
                word_first_fixation_duration = 'NA'
                word_first_char_dwell = 'NA'
                word_total_fix_time = 'NA'

            word_data = [[trial_no, trial_data.speechid.values[0], trial_data.paragraphid.values[0], w, word_map[w], word_fixated, number_of_fixations, word_landing_position, word_first_fixation_duration, word_first_char_dwell, word_total_fix_time]]
            word_data_df = pd.DataFrame(word_data, columns=['trialId','speechId', 'paragraphId', 'wordId', 'word', 'word_fixated', 'number_of_fixations', 'word_landing_position', 'word_first_fixation_duration', 'word_first_char_dwell', 'word_total_fix_time'])
            #word_df.append(word_data_df)
            word_df = pd.concat([word_df, word_data_df])
        #print("---")
    word_df.to_csv("word_feature_reports/"+subject+"_word_features.csv", index=False)
