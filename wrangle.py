import env
import os
import pandas as pd
import numpy as np

def get_zillow():
    '''
    function to retrieve zillow database information.  If cached file exists load that
    otherwise query database and cache the file
    '''
    filename = "zillow.csv"

    # if file is available locally, read it
    if os.path.isfile(filename):
        return pd.read_csv(filename)

    else:
       # if file not available locally, acquire data from SQL database
       # and write it as csv locally for future use 
       url = env.get_url(env.user, env.host, env.password, database='zillow')
       df = pd.read_sql('''
                            SELECT parcelid, bedroomcnt, bathroomcnt, calculatedfinishedsquarefeet, taxvaluedollarcnt, 
                                   yearbuilt, taxamount, fips
                            FROM properties_2017
                            LEFT JOIN propertylandusetype
                            USING (propertylandusetypeid)
                            WHERE propertylandusedesc = 'Single Family Residential' ''', url)
       # Write that dataframe to disk for later. This cached file will prevent repeated large queries to the database server.
       df.to_csv(filename, index=False)

       return df

def prep_zillow(df):
       '''
       function to prepare zillow data for exploration
       accepts a dataframe and returns the dataframe after deleting all 
       rows with null values
       '''
       df = df.dropna()
       return df