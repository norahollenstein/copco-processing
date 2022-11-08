import pandas as pd
from ast import literal_eval

word2char_mapping = pd.read_csv("word2char_IA_mapping-new-test.csv", converters={"characters": literal_eval, "char_IA_ids": literal_eval})
#word2char_mapping = pd.read_csv("word2char_IA_mapping.csv", converters={"characters": literal_eval, "char_IA_ids": literal_eval})

sents = word2char_mapping.groupby("sentenceId")


count = 0
for id, sent in sents:
  if len(sent) > 50:
    count += 1
    text_list = list(sent["word"])
    full_text = " ".join(text_list)
    #print(len(sent), full_text)
print(count)

count = 0
for id, sent in sents:
  if len(sent) < 3:
    count += 1
    text_list = list(sent["word"])
    full_text = " ".join(text_list)
    print(len(sent), full_text)
print(count)
