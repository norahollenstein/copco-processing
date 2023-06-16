import numpy as np
from collections import Counter

def get_experiment_part(speechid):
    """The texts of the CopCo corpus were split into two experiment parts. At the beginning of each recording one part was selected randomly."""
    # only danske taler speeches
    #experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946, 22811, 26682], "2": [1317, 1125, 7856, 10365, 1323, 7797, 1165, 1318, 10440, 17526]}
    # with wikipedia articles
    experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946, 22811, 26682, 202150, 202151, 202152, 202204, 202205, 202206], "2": [1317, 1125, 7856, 10365, 1323, 7797, 1165, 1318, 10440, 17526, 202201, 202202, 202203, 202207, 202208, 202209]}
    for k,v in experiment_parts.items():
        if speechid in v:
            part = k
    return part

def split_sentences(data):
    """Split the stimulus texts into sentences at the most common punctuation signs"""
    sentence_ids = []
    SENT_ID = 0
    sent_end_symbols = ("?", ".", "!", "?'", "!'", ":")

    for idx, row in data.iterrows():
        sentence_ids.append(SENT_ID)
        # nothing to do for the last word
        if idx != len(data)-1:
            if row.paragraphId != data.iloc[idx+1]['paragraphId']:
                SENT_ID += 1
            elif row.word.endswith(sent_end_symbols) and (data.iloc[idx+1]['word'][0].isupper() or data.iloc[idx+1]['word'][0] == "'"):
                SENT_ID += 1

    sent_lengths = Counter(sentence_ids)
    print("mean sent. length:", np.mean(list(sent_lengths.values())))
    print("number of sents:", len(list(set(sentence_ids))))
    return sentence_ids
