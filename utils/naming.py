import os
import re


session_name_pattern = re.compile(r'\A.*(?P<subject_id>\d{3})'
                                  r'_(?P<session_id>\d{1})'
                                  r'_(?P<session_type>[a,b,s])'
                                  r'(_(?P<experiment_name>[a-z]+))?'
                                  r'([.](?P<extension>[a-z]{3}))?\Z')


def get_subject_id(name: str) -> str:
    """
    Subject ID will be extracted from file or directory name.
    """
    return name.split('_')[0]


def get_session_id(name: str) -> str:
    """
    Session ID will be extracted from file or directory name.
    """
    return name.split('_')[1]


def get_session_type(name: str) -> str:
    """
    Session type will be extracted from file or directory name.
    """
    return os.path.splitext(name.split('_')[2])[0]


def get_session_infos(path: str) -> (str, str, str):
    """
    Get triple of subject_id, session_id and session_type.

    Infos will be extracted from file or directory name.

    """
    match = session_name_pattern.match(path)
    
    subject_id = match.group('subject_id')
    session_id = match.group('session_id')
    session_type = match.group('session_type')
    experiment_name = match.group('experiment_name')

    return subject_id, session_id, session_type, experiment_name


def get_session_name(path: str) -> str:
    """
    Get session name from file or directory path.
    """
    return os.path.splitext(os.path.basename(path))[0]


def create_session_name_from_session_info(subject_id: int,
                                          session_id: int,
                                          session_type: str):
    """
    Create session name of the form
    {subject_id}_{session_id}_{session_type}

    subject_id will be padded to digits.

    """
    return f'{subject_id:03}_{session_id}_{session_type}'


def create_path_for_results_dir(basepath: str,
                                subject_id: int,
                                session_id: int,
                                session_type: str) -> str:
    """
    Create path of the form {basepath}/{subject_id}_{session_id}_{session_type}

    subject_id will be padded to digits.

    """
    dirname = f'{int(subject_id):03}_{session_id}_{session_type}'
    filepath = os.path.join(basepath, dirname)
    return filepath


def create_filepath_for_csv_file(basepath: str,
                                 subject_id: int,
                                 session_id: int,
                                 session_type: str,
                                 experiment_type: str) -> str:
    """
    Create filepath of the form
    {basepath}/{subject_id}_{session_id}_{session_type}_{experiment_type}.csv

    subject_id will be padded to digits.

    """
    filename = f'{int(subject_id):03}_{session_id}_{session_type}_{experiment_type}.csv'
    filepath = os.path.join(basepath, filename)
    return filepath


def create_filepath_for_asc_file(basepath: str,
                                 subject_id: int,
                                 session_id: int,
                                 session_type: str) -> str:
    """
    Create filepath of the form
    {basepath}/{subject_id}_{session_id}_{session_type}.asc

    subject_id will be padded to digits.

    """
    filename = f'{int(subject_id):03}_{session_id}_{session_type}.asc'
    filepath = os.path.join(basepath, filename)
    return filepath
