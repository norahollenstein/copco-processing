# CopCo Eye-Tracking Data Processing

This repository contains the code to analyze and post-process the eye-tracking data of the CopCo corpus, which is described in the following publication:

Nora Hollenstein, Maria Barrett, and Marina Björnsdóttir. 2022. [The Copenhagen Corpus of Eye Tracking Recordings from Natural Reading of Danish Texts](https://aclanthology.org/2022.lrec-1.182/). In _Proceedings of the Thirteenth Language Resources and Evaluation Conference_, pages 1712–1720, Marseille, France. European Language Resources Association.

Please make sure to read about the data format and download the latest version of the data from the [OSF repository](https://osf.io/ud8s5/).

## Participant statistics
`python participant_statistics.py RawData/`  
This script includes calculation of comprehension scores and overall reading times. Raw Data should include one folder per participant containing the respective EDF recording file.

`python calibration_check.py`  
This script checks the calibration accuracy of all participants.

## Dataset statistics
`python texts_statistics.py`  
This script includes calculation of text and sentence length.

## Feature extraction from fixation and interest area reports

The extracted features can be found in `ExtractedFeatures/`, but if required you can also re-run the code to add additional features or modify the existing ones:

1. Use the DataViewer software from SR Research to convert the recorded EDF files to fixation reports and interest area reports in TXT format.  

2. If the reports were exported in utf-8 encoding (this can be speficied in the DataViewer preferences), this step can be skipped.  
Convert SR DataViewer output files to UTF-8 for correct representation of Danish special characters:  
`iconv -f ISO-8859-1 -t UTF-8 FIX_report_P10.txt > FIX_report_P10-utf8.txt`  
`iconv -f ISO-8859-1 -t UTF-8 IA_report_P10.txt > IA_report_P10-utf8.txt`  

These files are also available in the [OSF repository](https://osf.io/ud8s5/) (original and UTF-8 versions) in the folders FixationReports and InterestAreaReports.

3. Create a mapping from character interest areas to word interest areas:  
`python char2word_mapping.py`  
This step is only required if there were changes in the experiment setup. In order to complete this step it is necessary to deploy the experiment in the SR ExperimentBuilder twice, once with automatic segmentation of text into individual characters as areas of interest, and once with word segmentation as areas of interest. The required files are provided in `aois/`. The script `char2word_mapping.py` will align the characters to the words.

4. Extract word-level and character-level features with
`python extract_features.py`  
This outputs new CSV files in `ExtractedFeatures/`.  
These files can also be downloaded directly from the [OSF repository](https://osf.io/ud8s5/).

A description of the extracted features can be found [here](https://osf.io/ud8s5/wiki/Eye-tracking%20features/).



## Data validation

Use the script `validate_data.py` to check the data quality, e.g., word length effect and landing position analysis.

Use the script `participant_correlations.py` to calculate correlations between different participants characteristics.

## Dyslexia classification

This directory contains the code used for the dyslexica classification methods described in the following publication:

Marina Björnsdóttir, Nora Hollenstein, and Maria Barrett, 2023. Dyslexia Prediction from Natural Reading of Danish Texts. In _Proceedings of the 24th Nordic Conference on Computational Linguistics_, pages 1712–1720, Torshavn, Faroe Islands. 
