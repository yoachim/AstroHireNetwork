import numpy as np
import glob
import pandas as pd

# Check how well we recover the known Hubble Fellows


def restore_db():
    filenames = glob.glob('phd_store*.h5')
    data_df = pd.read_hdf(filenames[0], 'author_df')
    for filename in filenames[1:]:
        temp = pd.read_hdf(filename, 'author_df')
        data_df = data_df.append(temp, ignore_index=True)

    # make a dataframe that is just US astro PhDs
    astro_df = data_df[(data_df['nonUS'] == False) &
                       (data_df['astroPublication'] == True)]
    return astro_df, data_df


def check_hubble():

    names = ['name', 'inst']
    types = ['|S40', '|S50']
    dtypes = list(zip(names, types))
    hubbleData = np.genfromtxt('hubble_clean.dat', delimiter='\t', dtype=dtypes, comments='#')

    # make a list that is FA, last name, year
    good_fellows = []
    for fellow in hubbleData:
        year = int(fellow['inst'].rstrip().split(' ')[-1])
        if (year >= 1997) & (year <= 2013):
            name = fellow['name'].split(' ')
            good_fellows.append('%s, %s, %i' % (name[0][0], name[1], year))

    return good_fellows


if __name__ == '__main__':

    db, full_db = restore_db()
    gf = check_hubble()
    full_list = []
    for au, year in zip(db.author, db.phd_year):
        name = au.split(',')
        full_list.append('%s, %s, %i' % (name[1][1], name[0], year))

    not_in = []
    for entry in gf:
        if entry not in full_list:
            not_in.append(entry)


    # Looks like some of the phd years do not agree
    only_names = [entry[:-6] for entry in full_list]

    still_not_in = []
    for entry in not_in:
        if entry[:-6] not in only_names:
            still_not_in.append(entry)

    frac_recovered =1. - len(still_not_in)/float(len(gf))
    print 'recovered %f %% of the Hubble Fellows (%i of %i)' % (frac_recovered, len(gf)-len(still_not_in), len(gf))

    # Go through and decide why the 22 did not get picked up. Some combination of phd not in ADS, name got mangled, failed
    # to ID as an astronomer, or did not ID as a USA institution.
    

