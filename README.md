# CopCo Eye-Tracking Data Processing

## Participant statistics
participant_statistics.py  
This script includes calculation of comprehension scores and overall reading times.

## Dataset statistics
speech_statistics.py
This script includes calculation of text and sentence length.

## Feature extraction from fixation reports

1. Convert SR DataViewer output files to UTF-8 for correct representation of Danish characters:  
`iconv -f ISO-8859-1 -t UTF-8 FIX_report_P10.txt > FIX_report_P10-utf8.txt`

2. Create a mapping from character interest areas to word interest areas:
`char2word_mapping.py`

3. Extract word-level and character-level features
extract_features.py
This outputs new files in 'ExtractedFeatures/'.
These files can also be downloaded directly from the OSF repository.



## Data validation

Use the script validate_data.py to check the data quality, e.g., word length effect.


