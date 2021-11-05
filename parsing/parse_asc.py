#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Eyetracking-Data extraction
Experiments: PVT, Reading, JumpingPoints 2019
This script extracts the lines with samples (timestamp, x-screen coordinate, y-screen coordinate, pupil diameter)
from Eyelink 100 raw data files (previously converted from edf to ascii).

Extract recording samples on experimental trials; 
remove samples on practice trials and on game trials;
remove samples between trials (calibration)

Author: Lena Jäger
Edited by: Patrick Haller (October 2020),
           Daniel Krakowczyk (November 2020)
'''
import re
import os
import codecs
import logging
from collections import defaultdict
from typing import Dict, List, Union

import pandas as pd
import numpy as np

from parsing.constants import max_judo_trial_id
import parsing.message_patterns as mp

from utils.naming import create_filepath_for_csv_file
from utils.naming import get_subject_id, get_session_id, get_session_type


def check_file(filename):
    # files to exclude from parsing (e.g., aborted sessions):
    black_list = [] # add all files that were aborted but repeated under a different file name
    # Grund fuer Abbrüche in Probandendaten checken
    
    if filename in black_list:
        logging.info(f'Parsing of file {filename} was not completed because file is on black list (e.g., aborted session).')
        return 0
    # handling mistakes in file names
    #elif re.compile('0057-.*.asc').match(file):  # recode subject_id 57 followed by hyphen as subject_id 0 (subject_id 57_ already exists)
    #    subject_id = 0
    #    session_id = int(file.split('-')[1].split('.')[0])  # session was coded correctly

    # treat cases [0-9]^4-[0-9].asc and [0-9]^4_[0-9]_[0-9].asc
    elif len(filename.split('_')) == 2:
        subject_id = int(filename.split('_')[0]) # reader id
        session_id = (filename.split('_')[1].split('.')[0])# session
        session_type = ''
    elif len(filename.split('_')) == 1 and len(filename.split('-')) == 2:
        subject_id = int(filename.split('-')[0])
        session_id = (filename.split('-')[1].split('.')[0])
        session_type = ''
    elif len(filename.split('_')) == 3:
        subject_id = int(get_subject_id(filename))
        session_id = int(get_session_id(filename))
        session_type = get_session_type(filename)
    else:
        logging.error(f'unknown file name format: {filename}. could not extract subject and session id.')
        return 0
    
    return (subject_id, session_id, session_type)


def parse_asc_file(filename: str,
                   path_asc_files: Union[str],
                   path_csv_files: Union[str],
                   experiments: List[str],
                   columns: Union[str, Dict[str, str]],
                   check_file_exists: bool = True):
    logging.basicConfig(format='%(levelname)s::%(message)s',
                        level=logging.INFO)
    logging.info(f'parsing file {filename}')

    if check_file(filename) == 0:
        return 0
    else:
        (subject_id, session_id, session_type) = check_file(filename)
     
    # pvt
    pvt_block_id = 0
    pvt_trial_id = -1
    pvt_colour = -1     # colors: 1=black, 2=red, 3=green
    pvt_practice = 0
    
    # reading
    reading_screen = -1
    reading_question = -1
    reading_trial_id = 0
    reading_text_id = -1
    
    # judo
    judo_trial_id = -1
    judo_point_id = -1
    judo_ambig = -1
    
    # karolinska
    karo_block_id = 0

    # STORING
    data_out = defaultdict(lambda: defaultdict(list))
    select = False  # true if next eyetracking sample should be written out
    curr_exp = ''   # current experiment to write sample for
    
    asc_file = codecs.open(os.path.join(path_asc_files, filename),
                           'r', encoding='ascii', errors='ignore')

    line = True
    while line:
        try:
            line = asc_file.readline()
        except UnicodeDecodeError:
            logging.error(f'DECODING ERROR, aborting file {filename}')
            return -1

        if line.startswith('MSG'):
            # PVT
            if mp.on_pvt_block.match(line):
                select = False
                curr_exp = 'pvt'
                pvt_block_id += 1
                pvt_trial_id = 0
                pvt_practice = 0
            # match only to check if current pvt_block_id is correct
            elif mp.pvt_block_id.match(line):
                 m = mp.pvt_block_id.match(line)
                 read_pvt_block_id = int(m.group('block_id'))
                 if pvt_block_id != read_pvt_block_id:
                     logging.error(f'READ PVT BLOCK ID {read_pvt_block_id}'
                                   f' DID NOT MATCH EXPECTED BLOCK ID'
                                   f' {pvt_block_id}.'
                                   f' Aborting {filename}!')
                     return -1
            elif mp.off_pvt_block.match(line):
                select = False
                curr_exp = 'NA'
                pvt_block_id += 1
                pvt_trial_id = 0
                pvt_practice = 0

            # practice trial
            elif mp.on_pvt_practice.match(line):
                # checkpoint whether pvt block message was written
                if curr_exp == 'pvt':
                    # select will be set to true after driftcorrect message
                    pvt_practice = 1
                    pvt_trial_id = 0
                    pvt_colour = 0
                else:
                    logging.error('SYNCTIME PVT PRACTICE IS MISSING in file ', filename)
                    return -1
            elif mp.off_pvt_practice.match(line):
                select = False
                curr_exp = 'NA'
                pvt_practice = 0
            # data points recorded after pvt black message
            elif mp.on_pvt_practice_black.match(line):
                pvt_colour = 1
            # data points recorded after pvt black stop message
            elif mp.off_pvt_practice_black.match(line):
                pvt_colour = 0
            # data points recorded after synctime pvt red message
            elif mp.on_pvt_practice_red.match(line):
                pvt_colour = 2
            # data points recorded after synctime pvt red stop message
            elif mp.off_pvt_practice_red.match(line):
                pvt_colour = 0
            # data points recorded after synctime green message
            elif mp.on_pvt_practice_green.match(line):
                pvt_colour = 3
            # data points recorded after synctime green stop message
            elif mp.off_pvt_practice_green.match(line):
                pvt_colour = 0
                
            # actual pvt trials
            elif mp.on_pvt_trial.match(line):
                if select is False:
                    select = True
                    curr_exp = 'pvt'
                    pvt_trial_id += 1
                    pvt_colour = 0
                else:
                    logging.error(f'PVT PRACTICE OFF MESSAGE IS MISSING!'
                                  f' Aborting file {filename}.')
                    return -1
            elif mp.off_pvt_trial.match(line):
                select = False
                curr_exp = 'NA'
            elif mp.pvt_trial_id.match(line):
                m = mp.pvt_trial_id.match(line)
                if pvt_trial_id !=  int(m.group('trial_id')):
                    logging.error('READ PVT TRIAL ID DID NOT MATCH'
                                  ' EXPECTED BLOCK ID. Aborting {filename}!')
                    return -1
            elif mp.on_pvt_black.match(line):
                # pvt practice block for color codes
                if curr_exp == 'pvt':
                    pvt_colour = 1
                else:
                    logging.error('WRITE OUT != PVT, aborting processing file', filename)
                    return -1
            elif mp.off_pvt_black.match(line):
                if curr_exp == 'pvt' and pvt_colour == 1:
                    pvt_colour = 0
                else:
                    logging.error('WRITE OUT != PVT, aborting processing file', filename)
                    return -1
            elif mp.on_pvt_red.match(line):
                if curr_exp == 'pvt'and pvt_colour == 0:
                    pvt_colour = 2
                else:
                    logging.error('WRITE OUT != PVT, aborting processing file', filename)
                    return -1
            elif mp.off_pvt_red.match(line):
                if curr_exp == 'pvt' and pvt_colour == 2:
                    pvt_colour = 0
                else:
                    logging.error('WRITE OUT != PVT, aborting processing file', filename)
                    return -1
            elif mp.on_pvt_green.match(line) and pvt_colour == 0:
                if curr_exp == 'pvt':
                    pvt_colour = 3
                else:
                    logging.error('WRITE OUT != PVT, aborting processing file', filename)
                    return -1
            elif mp.off_pvt_green.match(line):
                if curr_exp == 'pvt' and pvt_colour == 3:
                    pvt_colour = 0
                else:
                    logging.error('WRITE OUT != PVT, aborting processing file', filename)
                    return -1
            elif mp.off_pvt.match(line):
                select = False
                curr_exp = 'NA'
                pvt_practice = -1
                
            ## READING
            elif mp.on_reading.match(line):
                curr_exp = 'reading'
                select = False
                reading_screen = 0
                reading_question = 0
                reading_text_id = -1
            elif mp.on_reading_trial.match(line):
                # set current experiment again because of karolinska block
                # select will be set to true after driftcorrect message
                curr_exp = 'reading'
                select = False
                reading_trial_id += 1
                reading_screen = 0
                reading_question = 0
                reading_text_id = -1
            elif mp.on_screen.match(line):
                if select == True:
                    if reading_screen == 0:
                        m = mp.on_screen.match(line)
                        reading_screen = int(m.group('screen_id'))
                    else:
                        logging.error('MISSING READING SCREEN OFF MESSAGE. Aborting file ', filename)
                        return -1
                else:
                    logging.error('MISSING SYNCTIME TEXT MESSAGE. Aborting file, ', filename)
                    return -1
            elif mp.off_screen.match(line):
                # screen_id = 0 represents period between two screens
                reading_screen = 0
                select = False
            elif mp.on_question.match(line):
                curr_exp = 'reading'
                select = True
                m = mp.on_question.match(line)
                reading_question = int(m.group('question_id'))
            elif mp.on_question_id(10).match(line):
                curr_exp = 'reading'
                select = True
                reading_question = 10
            elif mp.off_question.match(line):
                reading_question = 0
            elif mp.off_reading.match(line):
                curr_exp = 'NA'
                select = False
            elif mp.text_id.match(line):
                # This works only because the trial vars are dumped after each eyetracking recording.
                # During the first recording of each trial (header screen) the text id will therefore be wrong.
                # For getting correct text ids during the header, there will be a workaround necessary
                # to go back in time with the text id information available just now.
                m = mp.text_id.match(line)
                reading_text_id = int(m.group('text_id'))
                
            # Judo
            elif mp.on_judo.match(line):
                if select == False:
                    curr_exp = 'judo'
                    judo_trial_id = 0
                else:
                    logging.error('MISSING KAROLINSKA STOP MESSAGE in file ', filename)
                    return -1
            elif mp.on_judo_trial.match(line):
                judo_point_id = 0
                if -1 < judo_trial_id < max_judo_trial_id:
                    # select will be set to true after driftcorrect message
                    curr_exp = 'judo'
                    judo_ambig = 1
                    judo_trial_id += 1

            elif mp.off_judo_trial.match(line):
                if judo_point_id == 5:
                    select = False
                    judo_point_id = 0
                else:
                    logging.error(f'SYNCTIME.P5 message is missing in file {filename}. Aborting.')
                    return -1
                  
            elif mp.on_judo_point.match(line):
                judo_ambig = 0
                m = mp.on_judo_point.match(line)
                p = int(m.group('point_id'))

                if not p-1==judo_point_id:
                    logging.error(f'Synctime message P{p} is missing in file {filename}. Aborting.')
                    logging.error(f'{line}')
                    logging.error(m.group('point_id'))
                    return -1
                else:
                    judo_point_id = p
                    
            elif mp.off_judo_point.match(line):
                # some data points are between p-1 and p's stop and start message 
                judo_ambig = 1
                
            elif mp.off_judo.match(line):
                select = False
                curr_exp = 'NA'
                
            # Karolinska Block inbetween PVT and Reading
            elif mp.on_karolinska.match(line):
                    select = True
                    curr_exp = 'karolinska'
                    karo_block_id += 1
                    # some block ids are wrongly skipped in actual experiment
                    if karo_block_id in [12, 14, 16]:
                        karo_block_id += 1
            elif mp.off_karolinska.match(line):
                select = False
                curr_exp = 'NA'

            # mandatory driftcorrects
            elif mp.driftcorrect.match(line):
                check_driftcorrect = (
                    (curr_exp in 'judo')
                    or (curr_exp == 'pvt' and pvt_practice == 1)
                    or (curr_exp == 'reading' and reading_screen == 0)
                )
                
                if check_driftcorrect:
                    if select:
                        time = mp.driftcorrect.match(line).group('time')
                        logging.error(f'UNEXPECTED DRIFTCORRECT OCCURED'
                                      f' DURING TRIAL AT TIMESTEP {time}!'
                                      f' Aborting {filename}!')
                        return -1
                    select = True

                    # driftcorrects occur always twice at a time
                    next_line = asc_file.readline()
                    if not mp.driftcorrect.match(next_line):
                        logging.error(f'SECOND DRIFTCORRECT EXPECTED BUT NOT'
                                      f' READ AFTER TIMESTEP {time}!'
                                      f' Aborting {filename}!')
                        return -1
                        
        # if line is a sample (not a message)
        elif select:
            if curr_exp not in experiments:
                continue
            m = mp.eye_tracking_sample.match(line)
            if not m:
                continue

            # write recorded samples into dictionary
            for column in columns['sample']:
                value = m.group(column)
                if column == 'time':
                    try:
                        value = int(value)
                    except:
                        logging.error(f'TIMESTAMP COULD NOT BE CASTED AS'
                                      f' INTEGER! Aborting {filename}!')
                        return -1
                else:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = np.nan
                data_out[curr_exp][column].append(value)

            # write experiment specific data into dictionary
            if curr_exp == 'pvt':
                data_out[curr_exp]['block_id'].append(pvt_block_id)
                data_out[curr_exp]['trial_id'].append(pvt_trial_id)
                data_out[curr_exp]['colour'].append(pvt_colour)
                data_out[curr_exp]['practice'].append(pvt_practice)

            elif curr_exp == 'reading':
                data_out[curr_exp]['trial_id'].append(reading_trial_id)
                data_out[curr_exp]['screen_id'].append(reading_screen)
                data_out[curr_exp]['question_id'].append(reading_question)
                data_out[curr_exp]['text_id'].append(reading_text_id)

            elif curr_exp == 'judo':
                data_out[curr_exp]['trial_id'].append(judo_trial_id)
                data_out[curr_exp]['point_id'].append(judo_point_id)
                data_out[curr_exp]['ambiguous'].append(judo_ambig)

            elif curr_exp == 'karolinska':
                data_out[curr_exp]['block_id'].append(karo_block_id)

        else:
            #TODO: Check what types of lines we are discarding here
            pass

    asc_file.close()

    for experiment in experiments:
        filepath = create_filepath_for_csv_file(
            basepath=path_csv_files,
            subject_id=subject_id,
            session_id=session_id,
            session_type=session_type,
            experiment_type=experiment)

        logging.info(f'writing {experiment} to {filepath}')

        file_columns = columns[experiment] + columns['sample']
        df = pd.DataFrame(data=data_out[experiment])
        df[file_columns].to_csv(filepath, index=False, sep='\t', na_rep='NaN')

    return 0
