# CopCo Eye-Tracking Data Processing

## Participant statistics
`python participant_statistics.py RawData/`  
This script includes calculation of comprehension scores and overall reading times. 

`python calibration_check.py`  
This script checks the calibration accuracy of all participants. 

## Dataset statistics
`python speech_statistics.py`  
This script includes calculation of text and sentence length.

## Feature extraction from fixation reports

1. Convert SR DataViewer output files to UTF-8 for correct representation of Danish characters:  
`iconv -f ISO-8859-1 -t UTF-8 FIX_report_P10.txt > FIX_report_P10-utf8.txt`

2. Create a mapping from character interest areas to word interest areas:  
`char2word_mapping.py`

3. Extract word-level and character-level features with
`extract_features.py`  
This outputs new files in `ExtractedFeatures/`.  
These files can also be downloaded directly from the [OSF repository](https://osf.io/ud8s5/).

A description of the extracted features can be found [here](https://osf.io/ud8s5/wiki/Eye-tracking%20features/).



## Data validation

Use the script `validate_data.py` to check the data quality, e.g., word length effect.


