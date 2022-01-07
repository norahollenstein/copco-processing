import os
import pandas as pd
from ast import literal_eval

# read interest area reports and convert character-level fixation into word-level gaze features

def get_part(speechid):
    #print(speechid)
    experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946, 22811, 26682], "2": [1317, 1125, 7856, 10365, 1323, 7797, 1165, 1318, 10440, 17526]}
    for k,v in experiment_parts.items():
        if speechid in v:
            part = k
    return part

report_dir = "IA_Reports_utf8/"
for file in os.listdir(report_dir)[:2]:
    print(file)
    if file.endswith(".txt"):
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

            trial_fixation_nos = 0

            for w, chars in word2char.items():
                #print(w, chars)

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

                    # todo: based on IA_FIRST_FIXATION_PREVIOUS_IAREAS	IA_FIRST_FIXATION_RUN_INDEX	or IA_FIRST_FIX_PROGRESSIVE, find out if there were regression to previous words or regressions from latter words to current word

                    # gaze duration (GD): the sum of all fixations on the current word in the first-pass reading before the eye moves out of the word = FPRT (first-pass reading time)
                    # go-past time (GPT): the sum of all fixations prior to progressing to the right of the current word, including regressions to previous words that originated from the current word

                    # no regressions to any previous chars (within the word or to previous words)
                    if (all_chars['IA_REGRESSION_OUT'].astype(str).astype(int) == 0).all():
                        # no regressions into any char of this word from later IAs = only 1 pass on the full word
                        if (all_chars['IA_REGRESSION_IN'].astype(str).astype(int) == 0).all():
                            word_go_past_time = word_total_fix_time
                            word_gaze_duration = word_total_fix_time
                        # multiple runs on at least one chars
                        else:
                            # GD < TFT
                            # TODO: assumption in the next line is not correct? check!!
                            # GPT = GD
                            print("HH-EE-RR-EE-----------")
                            for fix_index, fix in all_chars.iterrows():
                                word_gaze_duration = fix['IA_DWELL_TIME']
                                word_go_past_time = fix['IA_DWELL_TIME']
                                previous_fix = trial_data[trial_data['IA_FIRST_FIXATION_INDEX'] == str(int(fix['IA_FIRST_FIXATION_INDEX'])-1)]
                                print(fix['IA_ID'], previous_fix['IA_ID'])
                                print(word_fix_sequence)
                                # check if previous fixation falls within the current word
                                if previous_fix['IA_ID'].tolist()[0] in word_char_ids:
                                    print("------prev fix is within current word IA-----")
                                    word_gaze_duration += previous_fix['IA_DWELL_TIME']
                                # check if interest area of previous fixation is in a earlier word
                                elif previous_fix['IA_ID'].tolist()[0] < min(word_char_ids):
                                    # include regression to previous word in GPT
                                    print("------prev fix is BEFORE current word IA-----")
                                    word_go_past_time += previous_fix['IA_DWELL_TIME']
                                # check if interest area of previous fixation is in a later word
                                elif previous_fix['IA_ID'].tolist()[0] > max(word_char_ids):
                                    print("------prev fix is after current word IA-----")


                            print(word_total_fix_time, word_gaze_duration, word_go_past_time)

                    #at least one regression within the word or to previous words
                    else:
                        # no regressions into any char of this word from lates IAs = only 1 pass on the full word
                        if (all_chars['IA_REGRESSION_IN'].astype(str).astype(int) == 0).all():
                            # GPT = TFT
                            # GD < TFT
                            word_gaze_duration = "TBD"
                            word_go_past_time = word_total_fix_time
                        # multiple runs on at least one chars
                        else:
                            # GD < GPT < TFT
                            word_gaze_duration = "TBD"
                            word_go_past_time = "TBD"
                            #print(w, chars)
                            #print(trial_data.loc[trial_data['IA_ID'].isin(chars), 'IA_LABEL'])
                            #print(first_char['IA_ID'])
                            #print(all_chars[['IA_ID', 'IA_LABEL', "IA_REGRESSION_IN", "IA_REGRESSION_OUT", "IA_REGRESSION_OUT_FULL"]])
                            #print("----")

                    # TODO: use INTEREST_AREA_FIXATION_SEQUENCE to find the order of fixated words
                    """
                    print(word_map[w])
                    print(word_char_ids)
                    print(all_chars[['IA_ID', 'IA_LABEL', 'IA_FIRST_FIXATION_INDEX', 'IA_FIRST_RUN_FIXATION_COUNT', 'IA_FIXATION_COUNT', 'IA_FIRST_FIXATION_PREVIOUS_IAREAS', 'IA_FIRST_FIXATION_RUN_INDEX', 'IA_FIRST_FIX_PROGRESSIVE']])
                    #print(all_chars['INTEREST_AREA_FIXATION_SEQUENCE'].values[0])
                    print(".....")
                    """



                else:
                    word_fixated = False
                    word_landing_position_char = 'NA'
                    word_landing_position_index = 'NA'
                    word_first_fixation_duration = 'NA'
                    word_first_char_dwell_time = 'NA'
                    word_total_fix_time = 'NA'
                    word_gaze_duration = 'NA'
                    word_go_past_time = 'NA'

                word_data = [[trial_no, trial_data.speechid.values[0], trial_data.paragraphid.values[0], w, word_map[w], word_fixated, number_of_fixations, word_landing_position_char, word_landing_position_index, word_first_fixation_duration, word_first_char_dwell_time, word_total_fix_time, word_gaze_duration, word_go_past_time]]
                word_data_df = pd.DataFrame(word_data, columns=['trialId','speechId', 'paragraphId', 'wordId', 'word', 'word_fixated', 'number_of_fixations', 'word_landing_position_char', 'word_landing_position_index', 'word_first_fixation_duration', 'word_first_char_dwell_time', 'word_total_fix_time', 'word_gaze_duration', 'word_go_past_time'])
                #word_df.append(word_data_df)
                word_df = pd.concat([word_df, word_data_df])

            # TODO: use TRIAL_FIXATION_COUNT to check if it is equal to the sum of number_of_fixations in trial
            # this is always less - check why
            if trial_fixation_nos <= trial_data['TRIAL_FIXATION_COUNT'].values[0]:
                print(trial_data['TRIAL_FIXATION_COUNT'].values[0]-trial_fixation_nos, " fixations outside of character interest areas")
            else:
                # sanitiy check
                print("WARNING: too many fixations detected!")

            #print("---")
        word_df.to_csv("word_feature_reports/"+subject+"_word_features.csv", index=False, encoding='utf-8')