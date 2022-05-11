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

The extracted features can be found in `ExtractedFeatures/`, but if required you can also re-run the code to add additional features: 

1. Use the DataViewer software from SR Research to convert the recorded EDF files to fixation reports in TXT format. 

2. Convert SR DataViewer output files to UTF-8 for correct representation of Danish special characters:  
`iconv -f ISO-8859-1 -t UTF-8 FIX_report_P10.txt > FIX_report_P10-utf8.txt`

3. Create a mapping from character interest areas to word interest areas:  
`python char2word_mapping.py`

In order to complete this step it is necessary to deploy the experiment in the SR ExperimentBuilder twice, once with automatic segmentation of text into individual characters as areas of interest, and once with word segmentation as areas of interest. The script `char2word_mapping.py` will align the characters to the words.

3. Extract word-level and character-level features with
`python extract_features.py`  
This outputs new CSV files in `ExtractedFeatures/`.  
These files can also be downloaded directly from the [OSF repository](https://osf.io/ud8s5/).

A description of the extracted features can be found [here](https://osf.io/ud8s5/wiki/Eye-tracking%20features/).



## Data validation

Use the script `validate_data.py` to check the data quality, e.g., word length effect and landing position analysis.


