
''' A module for loading flipper databases. '''

import pandas as pd
import flipper

import os

DATABASE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'censuses')
DATABASES = set(os.path.splitext(os.path.basename(path))[0] for path in os.listdir(DATABASE_DIRECTORY) if os.path.splitext(path)[1] == '.csv')

def census(census_name, reindex=True):
    ''' Return the requsted database.
    
    By default rows are indexed by the mapping torus name, this can be disabled by setting reindex=False. '''
    
    if census_name in DATABASES:
        census_name = os.path.join(DATABASE_DIRECTORY, census_name + '.csv')
    
    return pd.read_csv(census_name, index_col='manifold' if reindex else None)

