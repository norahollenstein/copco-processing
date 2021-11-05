#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from datetime import datetime
from joblib import Parallel, delayed
from typing import Dict, List, Union

import numpy as np

from utils.loading import load_config
from parsing.parse_asc import parse_asc_file


logging.basicConfig(format='%(levelname)s::%(message)s',
                    level=logging.INFO)


def process_asc_to_csv(path_asc_files: str,
                       path_csv_files: str,
                       experiments: List[str],
                       columns: Union[str, Dict[str, str]],
                       n_jobs: int = 1,
                       check_file_exists: bool = True):
    filenames = [filename for filename in os.listdir(path_asc_files)
                 if os.path.splitext(filename)[1] == '.asc']
    filenames.sort()
    logging.info(f'Input files ({len(filenames)}): {filenames}')

    # parse files in parallel
    done = Parallel(n_jobs=n_jobs)(
        delayed(parse_asc_file)(filename=filename,
                                path_asc_files=path_asc_files,
                                path_csv_files=path_csv_files,
                                experiments=experiments,
                                columns=columns,
                                check_file_exists=check_file_exists)
        for filename in filenames)

    return 0


def main():
    start_time = datetime.now()
    
    config = load_config()
    
    asc_path = config['eyetracking_asc_path']
    csv_path = config['eyetracking_csv_path']
    experiments = config['asc2csv']['experiments']
    columns = config['asc2csv']['columns']
    n_jobs = config['asc2csv']['n_jobs']
    check_file_exists = config['asc2csv']['check_file_exists']

    '''
    parse_asc_file(filename='001_1_a.asc',
                   path_asc_files=asc_path,
                   path_csv_files=csv_path,
                   experiments=experiments,
                   columns=columns,
                   check_file_exists=check_file_exists)
    '''
    process_asc_to_csv(path_asc_files=asc_path, path_csv_files=csv_path,
                       experiments=experiments, columns=columns,
                       n_jobs=n_jobs, check_file_exists=check_file_exists)

    logging.info(f'Took {datetime.now() - start_time}')


if __name__ == "__main__":
    main()
