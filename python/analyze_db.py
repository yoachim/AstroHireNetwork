import numpy as np
import pandas as pd


if __name__ == '__main__':

    # Read in the dataframe generated by generate_db.py
    author_df = pd.read_hdf('phd_store_2006.h5', 'author_df')
