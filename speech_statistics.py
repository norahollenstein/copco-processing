import os
import sys
import pandas as pd
import numpy as np
import spacy

# Calculate basic statistics for each speech

# usage: python speeches_statistics.py

def spacy_dk_pipeline(text):

    nlp = spacy.load("da_core_news_sm")
    tagged_text = nlp(text)

    return tagged_text


def get_freq_proportion(texts_df):
    """Calculates the proportion of words within the 10000 most common Danish words.
    Source frequency list: https://korpus.dsl.dk/resources/details/freq-lemmas.html"""

    dk_frequency_list = pd.read_csv("lemma-10k-2017/lemma-10k-2017-in.txt", delimiter="\t")

    freq_proportion = {}

    ids = texts_df["SpeechID"].unique()
    for id in ids:
        count_freq = 0
        toks = 0
        text = texts_df.loc[texts_df['SpeechID'] == id]
        text_list = list(text["Text"])
        for paragraph in text_list:
            tagged = spacy_dk_pipeline(paragraph)
            for token in tagged:
                toks += 1
                if token.lemma_ in list(dk_frequency_list['i']):
                    count_freq += 1

        freq_proportion[id] = count_freq/toks
        print(id, count_freq/toks)

    return freq_proportion


def main():

    speeches = pd.read_csv("df_experimental_speeches.tsv", delimiter="\t")

    frequency_prop = get_freq_proportion(speeches)


if __name__ == '__main__':
    main()
