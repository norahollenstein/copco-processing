import re


# line containing eyetracking sample
eye_tracking_sample = re.compile(r'(?P<time>\d*)\s+'
                                 r'(?P<x_left>[-]?\d*[.]\d*)\s+'
                                 r'(?P<y_left>[-]?\d*[.]\d*)\s+'
                                 r'(?P<pupil_left>\d*[.]\d*)\s+'
                                 r'(?P<x_right>[-]?\d*[.]\d*)\s+'
                                 r'(?P<y_right>[-]?\d*[.]\d*)\s+'
                                 r'(?P<pupil_right>\d*[.]\d*)\s*'
                                 r'((?P<dots>[A-Za-z.]{5}))?\s*$')


## PVT regex patterns
on_pvt = re.compile('.*SYNCTIME_PVT$')
off_pvt = re.compile(r'MSG\s+(?P<time>\d+)\s+[-]?\d+'
                     r'\s+PVT[.]STOP$')

on_pvt_block = re.compile(r'MSG\s+(?P<time>\d+)\s+[-]?\d+'
                          r'\s+SYNCTIME_PVT_BLOCK$')
off_pvt_block = re.compile('.*PVT_END$')

on_pvt_trial = re.compile(r'MSG\s+(?P<time>\d+)\s+SYNCTIME_PVT_TRIAL$')
off_pvt_trial = re.compile(r'MSG\s+(?P<time>\d+)\s+PVT_TRIAL[.]STOP$')

on_pvt_practice = re.compile('.*SYNCTIME_PVT_PRACTICE$')
off_pvt_practice = re.compile('.*PVT_PRACTICE[.]STOP$')

pvt_block_id = re.compile('.*PVT_BLOCK_ID (?P<block_id>.*)')
pvt_trial_id = re.compile('.*PVT_TRIAL_ID: (?P<trial_id>.*)')

on_pvt_practice_black =  re.compile('.*SYNCTIME_PVT_BLACK_PRACTICE$')
on_pvt_practice_red = re.compile('.*SYNCTIME_PVT_RED_PRACTICE$')
on_pvt_practice_green = re.compile('.*SYNCTIME_PVT_GREEN_PRACTICE$')

off_pvt_practice_black =  re.compile('.*PVT_BLACK_PRACTICE[.]STOP$')
off_pvt_practice_red = re.compile('.*BUTTON_PRESS_PVT_PRACTICE$')
off_pvt_practice_green = re.compile('.*PVT_GREEN_PRACTICE[.]STOP$')

on_pvt_black = re.compile('.*SYNCTIME_PVT_BLACK$')
on_pvt_red = re.compile('.*SYNCTIME_PVT_RED$')
on_pvt_green = re.compile('.*SYNCTIME_PVT_GREEN$')

off_pvt_black = re.compile('.*PVT_BLACK[.]STOP$')
off_pvt_red = re.compile('.*PVT_BUTTON_PRESS$')
off_pvt_green = re.compile('.*PVT_GREEN[.]STOP$')


## READING regex patterns
on_reading =  re.compile('.*SYNCTIME_READING$')
off_reading = re.compile('.* READING[.]STOP$')

on_reading_trial = re.compile('.*SYNCTIME_READING_TRIAL$')
off_reading_trial = re.compile('.*TRIAL_READING[.]STOP$')

on_reading_header = re.compile('.*SYNCTIME_HEADER$')
off_reading_header = re.compile('.*HEADER[.]STOP$')

on_screen = re.compile(r'.*SYNCTIME_READING_SCREEN_(?P<screen_id>[1-9]\d*)$')
off_screen = re.compile(r'.*READING_SCREEN_(?P<screen_id>[1-9]\d*)[.]STOP$')

on_question = re.compile(r'.*SYNCTIME_[Q]?(?P<question_id>[1-9]\d*)$')
off_question = re.compile(r'.*Q(?P<question_id>[1-9]\d*)[.]STOP$')

text_id = re.compile(r'MSG\s+(?P<timestamp>\d+) !V TRIAL_VAR textid (?P<text_id>\d+)')

def on_question_id(question_id: int) -> re.Pattern:
    if question_id == 10:
        return re.compile('.*SYNCTIME_[Q]?10$')
    else:
        return re.compile(f'.*SYNCTIME_[Q]?{question_id}$')

def off_question_id(question_id: int) -> re.Pattern:
    return re.compile(f'.*Q{question_id}[.]STOP$')

def on_screen_id(screen_id: int) -> re.Pattern:
    return re.compile(f'.*SYNCTIME_READING_SCREEN_{screen_id}$')

def off_screen_id(screen_id: int) -> re.Pattern:
    return re.compile(f'.*READING_SCREEN_{screen_id}[.]STOP$')


## JuDo regex patterns
on_judo = re.compile('.*SYNCTIME_JUDO$')
off_judo = re.compile('.*JUDO[.]STOP$')

on_judo_trial = re.compile(r'MSG\s+(?P<time>\d+)'
                           r'\s+SYNCTIME_JUDO_TRIAL$')
off_judo_trial = re.compile(r'MSG\s+(?P<time>\d+)'
                            r'\s+JUDO_TRIAL[.]STOP$')

on_judo_point = re.compile(r'MSG\s+(?P<time>\d+)\s+[-]?\d+'
                           r'\s+SYNCTIME[.]P(?P<point_id>\d+)$')
off_judo_point = re.compile(r'MSG\s+(?P<time>\d+)\s+[-]?\d+'
                           r'\s+P(?P<point_id>\d+)[.]STOP$')

def on_judo_point_id(point_id: int) -> re.Pattern:
    return re.compile(f'.*SYNCTIME[.]P{point_id}$')

def off_judo_point_id(point_id: int) -> re.Pattern:
    return re.compile(f'.*P{point_id}[.]STOP')


# KAROLINSKA regex patterns
on_karolinska = re.compile(r'MSG\s+(?P<time>\d+)\s+[-]?\d+'
                           r'\s+SYNCTIME_KAROLINSKA$')
off_karolinska = re.compile(r'MSG\s+(?P<time>\d+)'
                            r'\s+\d\s+KAROLINSKA[.]STOP$')

# ALCOHOL regex patterns
on_alcohol_test = re.compile(r'MSG\s+(?P<time>\d+)'
                             r'\s+SYNCTIME_ALCOHOL_TEST$')
off_alcohol_test = re.compile(r'MSG\s+(?P<time>\d+)\s+\d+'
                              r'\s+ALCOHOL_TEST[.]STOP$')

on_alcohol_consumption = re.compile(r'MSG\s+(?P<time>\d+)'
                                    r'\s+SYNCTIME_ALCOHOL_CONSUMPTION$')
off_alcohol_consumption = re.compile(r'MSG\s+(?P<time>\d+)\s+\d+'
                                     r'\s+ALCOHOL_CONSUMPTION[.]STOP$')

alcohol_measurement = re.compile(r'MSG\s+(?P<time>\d+)'
                                 r'\s+CURRENT_ALCOHOL_LEVEL: '
                                 r'(?P<promille>\d+([.]\d+)?)$')

# driftcorrect
driftcorrect_any = re.compile(r'MSG\s+(?P<time>\d+)\s+DRIFTCORRECT\s+.*$')

driftcorrect = re.compile(r'MSG\s+(?P<time>\d+)\s+DRIFTCORRECT\s+LR\s+'
                          r'(?P<eye>LEFT|RIGHT)\s+'
                          r'at\s+(?P<x_pos>\d+),(?P<y_pos>\d+)\s+'
                          r'OFFSET\s+(?P<offset_deg>[-]?\d+[.]\d+)\s+deg[.]\s+'
                          r'(?P<offset_x_pixel>[-]?\d+[.]\d+),'
                          r'(?P<offset_y_pixel>[-]?\d+[.]\d+) pix[.].*$')

driftcorrect_aborted = re.compile(r'MSG\s+(?P<time>\d+)\s+DRIFTCORRECT\s+LR\s+ABORTED$')

driftcorrect_repeating = re.compile(r'MSG\s+(?P<time>\d+)\s+DRIFTCORRECT\s+LR\s+'
                                    r'REPEATING due to large error\s+'
                                    r'L=(?P<left_error>[-]?\d+.\d+)\s+'
                                    r'R=(?P<right_error>[-]?\d+.\d+)\s+'
                                    r'drift_correction_maxerr=(?P<max_error>[-]?\d+.\d+).*$')

# video sync message
videosync = re.compile(r'MSG\s+(?P<time_msg>\d+)\s+'
                       r'(?P<uuid>[a-f0-9]{32})\s+'
                       r'(?P<time_sync>\d+[.]\d+)')
