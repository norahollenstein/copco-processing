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

    # reading time in seconds (sampling rate 1000Hz)
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

    for item in os.listdir(data_dir):
        if "P" in item:
            subject_id = item
            results_file_path = os.path.join(data_dir, item, 'RESULTS_FILE.txt')

            results = pd.read_csv(results_file_path, delimiter="\t")
            # remove practice trials
            results = results[results.condition != "practice"]
            # remove beginning of speech trials
            results = results[results.paragraphid != -1]

            #avg_accruacy, question_no = comprehension_score(results)
            #print(subject_id, avg_accruacy, question_no)

            abs_read_time, rel_read_time = reading_time(results)
            print(subject_id, abs_read_time, rel_read_time)


if __name__ == '__main__':
    main()
