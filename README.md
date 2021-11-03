# copco-processing
Code to process CopCo EyeLink files

## EyeLink data processing

### Step 1: Convert EDF to ASC files 
Option 1: using SR Research - EDF2ASC tool  
Optoin 2: convert_edf_files_to_asc.py (needs local installation of the tool?)

### Step 2: Convert ASC to CSV
Use run_asc2csv.sh

### Step 3: Fixation/saccade detection
Use saccade_detection.py 

### Step 4: Compute reading times per word
Adapt this script: https://osf.io/wku9c/ to compute reading time features from CSV
