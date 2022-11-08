import os
import pandas as pd

# fix interest areas of first and last line: these are always too short compared to the middle lines

for file in os.listdir('renamed_aois_aug22/'):
    if file.endswith(".ias"):
        print(file)
        ias = pd.read_csv('renamed_aois_aug22/'+file, delimiter="\t", header=None, index_col=False, names=["type", "number", "left", "top", "right", "bottom", "label"])
        #check if AOIs have more than one line
        if len(ias["top"].unique()) > 1:
            top_line_position = ias["top"].min()
            bottom_line_position = ias["bottom"].max()
            for index, row in ias.iterrows():
                #if row["top"] == ias.at[index+1,"top"]:
                if row["top"] == top_line_position:
                    ias.at[index,"top"] = int(ias.at[index,"bottom"] - 93)
                if row["bottom"] == bottom_line_position:
                    ias.at[index,"bottom"] = int(ias.at[index,"top"] + 93)

            print("---------")
        else:
            #fix AOIs with only one line
            #print(ias)
            top_line_position = ias["top"].min()
            bottom_line_position = ias["bottom"].max()
            midpoint = (bottom_line_position + top_line_position) / 2
            ias["top"] = int(midpoint - 47)
            ias["bottom"] = int(midpoint + 47)

        ias.to_csv("aois_fixed_aug22/"+file, index=False, header=False, sep="\t")
