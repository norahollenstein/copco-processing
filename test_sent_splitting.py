import pandas as pd
from ast import literal_eval

# This script checks for extremely long or short sentences in the CopCo data.

word2char_mapping = pd.read_csv("word2char_IA_mapping.csv", converters={"characters": literal_eval, "char_IA_ids": literal_eval})

speeches = word2char_mapping.groupby("speechId")
for id, speech in speeches:
    print(id, len(speech['sentenceId'].unique()))

print()
print()

sents = word2char_mapping.groupby("sentenceId")


count = 0
for id, sent in sents:
  if len(sent) > 80:
    count += 1
    text_list = list(sent["word"])
    full_text = " ".join(text_list)
    print(len(sent), full_text)
print(count)

print()
print()

count = 0
for id, sent in sents:
  if len(sent) < 3:
    count += 1
    text_list = list(sent["word"])
    full_text = " ".join(text_list)
    print(len(sent), full_text)
print(count)
