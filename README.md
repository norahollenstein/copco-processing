# CopCo Eye-Tracking Data Processing

## Participant statistics
participant_statistics.py  
includes calculation of comprehension scores and reading times

## Dataset statistics
speech_statistics.py

## Feature extraction from fixation reports

1. Convert DataViewer output files to UTF-8 for Danish special characters:
iconv -f ISO-8859-1 -t UTF-8 FIX_report_P10.txt > FIX_report_P10-utf8.txt

2. Create mapping from character interest areas to word interest areas:
char2word_mapping.py

3. Extract word-level and character-level features
extract_features.py
This outputs new files in ..



## Data validation
validate_data.py


