import pandas as pd
import numpy as np


def correct_fixation_mapping(trial_data_df, mALL_FIX, mUNMAPPED, mDIST):
    # map fixations that fall outside of interest areas but are close enough
    # use CURRENT_FIX_NEAREST_INTEREST_AREA_LABEL with a threshold on CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE
    #print(len(filtered))
    ALL_FIX += len(trial_data_df)

    # todo fix this: this is not correct, takes the original fixation report, rather than the filtered word data...
    unmapped = trial_data_df.loc[trial_data_df['CURRENT_FIX_INTEREST_AREAS'].str.len() == 0]
    unmapped['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE'] = unmapped['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE'].str.replace(',', '.').astype(float)
    UNMAPPED += len(unmapped)

    tiny_distance = unmapped.loc[unmapped['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE'] < 1]
    #print(len(tiny_distance))
    DIST += len(tiny_distance)


    #print(np.mean(unmapped['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE']))
    """
    print(np.std(unmapped['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE']))
    print(np.min(unmapped['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE']))
    print(np.max(unmapped['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE']))
    print("----------------")
    """

    return trial_data_df #, mALL_FIX, mUNMAPPED, mDIST
