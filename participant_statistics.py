import os
import sys
import pandas as pd
import numpy as np

# Calculate basic statistics for each participant
# Reads the file 'RESULTS_FILE.txt' generated for each participant by EyeLink

# usage: python participant_statistics.py /path/to/eyetrackingdata/

def comprehension_score(results_df):
    """Calculate the comprehension score (avergage accuracy of all answered questions)"""

    questions = results_df.loc[results_df['question'] != "NO QUESTION"]
    average_accuracy = sum(questions['QUESTION_ACCURACY'])/len(questions)

    return average_accuracy, len(questions)

def reading_time(results_df):
    """Extract the absolute reading time (seconds spent on each screen) and normalized by number of words on the screen"""

    # reading time per screen in seconds (sampling rate 1000Hz)
    absolute_reading_times = results_df['SENTENCE_RT']/1000
    avg_absolute_reading_times = np.mean(absolute_reading_times)

    relative_reading_times = []
    for t, a in zip(results_df['text'], absolute_reading_times):
        t = t.split()
        words = len(t)
        relative_reading_times.append(a/words)
    avg_relative_reading_times = np.mean(relative_reading_times)

    return avg_absolute_reading_times, avg_relative_reading_times


def main():

    data_dir = sys.argv[1]
    participant_stats = pd.DataFrame(columns=['subj', 'comprehension_accuracy', 'number_of_speeches', 'number_of_questions', 'absolute_reading_time', 'relative_reading_time'])
    speeches_read_all = []
    for item in os.listdir(data_dir):
        if "P" in item:
            speeches_read = []
            subject_id = item
            results_file_path = os.path.join(data_dir, item, 'RESULTS_FILE.txt')

            results = pd.read_csv(results_file_path, delimiter="\t")
            # remove practice trials
            results = results[results.condition != "practice"]
            # remove beginning of speech trials
            results = results[results.paragraphid != -1]

            avg_accruacy, question_no = comprehension_score(results)
            #print(subject_id, avg_accruacy, question_no)

            abs_read_time, rel_read_time = reading_time(results)
            #print(subject_id, abs_read_time, rel_read_time)

            speeches_read = list(set(results['speechid'].values))

            participant_stats = participant_stats.append({'subj': subject_id, 'comprehension_accuracy': "{:.2f}".format(avg_accruacy), 'number_of_speeches': len(speeches_read), 'number_of_questions': question_no, 'absolute_reading_time': "{:.2f}".format(abs_read_time), 'relative_reading_time':"{:.2f}".format(rel_read_time)}, ignore_index=True)
            speeches_read_all += speeches_read
    print(participant_stats)
    participant_stats.to_csv("participant_stats.csv", index=False)

    print("Total speeches read: ", len(speeches_read_all))
    print("Unique speeches read: ", len(set(speeches_read_all)))
    print(set(speeches_read_all))

    # how often each speech was read:
    speech_freq = {i:speeches_read_all.count(i) for i in set(speeches_read_all)}
    print(speech_freq)

if __name__ == '__main__':
    main()
