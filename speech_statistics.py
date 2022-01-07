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


def get_freq_proportion(text):
    """Calculates the proportion of words within the 10000 most common Danish words.
    Source frequency list: https://korpus.dsl.dk/resources/details/freq-lemmas.html"""

    dk_frequency_list = pd.read_csv("lemma-10k-2017/lemma-10k-2017-in.txt", delimiter="\t")

    count_freq = 0
    toks = 0
    text_list = list(text["Text"])
    for paragraph in text_list:
        tagged = spacy_dk_pipeline(paragraph)
        for token in tagged:
            toks += 1
            if token.lemma_ in list(dk_frequency_list['i']):
                count_freq += 1

    print(count_freq/toks)
    return round((count_freq/toks), 2)


def get_speech_length(text):
    """Calculates the number of sentences and number of words per sentence in a speeches_statistics."""

    text_list = list(text["Text"])
    full_text = " ".join(text_list)
    tagged = spacy_dk_pipeline(full_text)
    tokens_per_speech = len(tagged)
    types_per_speech = len(list(set([tok.text for tok in tagged])))
    types = list(set([tok.text for tok in tagged]))
    sentences = 0
    tokens = 0
    tokens_in_sent = []
    token_lenghts = []
    for ind, token in enumerate(tagged):
        token_lenghts.append(len(token.text))
        if token.is_sent_start:
            sentences += 1
            tokens = 1
        else:
            tokens += 1
        try:
            if tagged[ind+1].is_sent_start:
                tokens_in_sent.append(tokens)
        except IndexError:
            tokens_in_sent.append(tokens)

    tokens_per_sent = (round(np.mean(tokens_in_sent),2), round(np.std(tokens_in_sent),2), np.min(tokens_in_sent), np.max(tokens_in_sent))
    avg_token_length = (round(np.mean(token_lenghts),2), round(np.std(token_lenghts),2), np.min(token_lenghts), np.max(token_lenghts))
    return sentences, tokens_per_speech, types_per_speech, types, tokens_per_sent, avg_token_length, tokens_in_sent, token_lenghts


def main():

    speeches = pd.read_csv("df_experimental_speeches.tsv", delimiter="\t")

    speech_stats = pd.DataFrame(columns=['id', 'frequency_prop', 'number_of_sents', 'tokens_per_speech', 'types_per_speech', 'tokens_per_sent', 'avg_token_length'])

    ids = speeches["SpeechID"].unique()
    all_types = []
    all_tokens_in_sent = []
    all_token_lenghts = []
    for id in ids:
        print(id)
        speech = speeches.loc[speeches['SpeechID'] == id]
        frequency_prop = get_freq_proportion(speech)
        sentences, tokens_per_speech, types_per_speech, types, tokens_per_sent, avg_token_length, tokens_in_sent, token_lenghts = get_speech_length(speech)
        all_types += types
        all_tokens_in_sent += tokens_in_sent
        all_token_lenghts += token_lenghts
        speech_stats = speech_stats.append({'id': id, 'frequency_prop': frequency_prop, 'number_of_sents': sentences, 'tokens_per_speech':tokens_per_speech, 'types_per_speech':types_per_speech, 'tokens_per_sent':tokens_per_sent, 'avg_token_length':avg_token_length}, ignore_index=True)

    sorted_speech_stats = speech_stats.sort_values(by=["id"])
    print(sorted_speech_stats)
    print("MEANS/TOTAL:")
    print(all_token_lenghts)
    print(speech_stats['frequency_prop'].mean(), speech_stats['number_of_sents'].sum(), speech_stats['tokens_per_speech'].sum(), len(list(set(all_types))), np.mean(all_tokens_in_sent), np.std(all_tokens_in_sent), min(all_tokens_in_sent), max(all_tokens_in_sent), np.mean(all_token_lenghts), np.std(all_token_lenghts), min(all_token_lenghts), max(all_token_lenghts))
    sorted_speech_stats.to_csv("speech_stats.csv")


if __name__ == '__main__':
    main()
