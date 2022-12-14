from re import M
import env
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, QuantileTransformer


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

def my_split(df):
       '''
       Separates a dataframe into train, validate, and test datasets

       Keyword arguments:
       df: a dataframe containing multiple rows
       

       Returns:
       three dataframes who's length is 60%, 20%, and 20% of the length of the original dataframe       
       '''

       # separate into 80% train/validate and test data
       train_validate, test = train_test_split(df, test_size=.2, random_state=333)

       # further separate the train/validate data into train and validate
       train, validate = train_test_split(train_validate, 
                                          test_size=.25, 
                                          random_state=333)

       return train, validate, test

def remove_outliers(df, k, col_list):
    ''' remove outliers from a list of columns in a dataframe 
        and return that dataframe
    '''
    
    for col in col_list:

        q1, q3 = df[col].quantile([.25, .75])  # get quartiles
        
        iqr = q3 - q1   # calculate interquartile range
        
        upper_bound = q3 + k * iqr   # get upper bound
        lower_bound = q1 - k * iqr   # get lower bound

        # return dataframe without outliers
        
        df = df[(df[col] > lower_bound) & (df[col] < upper_bound)]
        
    return df

def scaler(scaler, train, validate, test):
       '''
       function accepts a scaler type, and train/validate/test dataframes then 
       performs scaling on the sq_ft and tax_amount columns
       returns the train, validate, and test dataframes with the additional 
       scaled columns
       '''
       

       train[['scaled_sqft', 'scaled_taxamount']] = scaler.fit_transform(train[['calculatedfinishedsquarefeet',
                                                                         'taxamount']])

       validate[['scaled_sqft', 'scaled_taxamount']] = scaler.transform(validate[['calculatedfinishedsquarefeet',
                                                                         'taxamount']])

       test[['scaled_sqft', 'scaled_taxamount']] = scaler.transform(test[['calculatedfinishedsquarefeet',
                                                                         'taxamount']])

       return train, validate, test

def wrangle_student_math(path):
    df = pd.read_csv(path, sep=";")

    # drop any nulls
    df = df[~df.isnull()]

    # get object column names
    object_cols = get_object_cols(df)

    # create dummy vars
    df = create_dummies(df, object_cols)

    # split data
    X_train, y_train, X_validate, y_validate, X_test, y_test = train_validate_test(
        df, "G3"
    )

    # get numeric column names
    numeric_cols = get_numeric_X_cols(X_train, object_cols)

    # scale data
    X_train_scaled, X_validate_scaled, X_test_scaled = min_max_scale(
        X_train, X_validate, X_test, numeric_cols
    )

    return (
        df,
        X_train,
        X_train_scaled,
        y_train,
        X_validate_scaled,
        y_validate,
        X_test_scaled,
        y_test,
    )

def get_object_cols(df):
    """
    This function takes in a dataframe and identifies the columns that are object types
    and returns a list of those column names.
    """
    # create a mask of columns whether they are object type or not
    mask = np.array(df.dtypes == "object")

    # get a list of the column names that are objects (from the mask)
    object_cols = df.iloc[:, mask].columns.tolist()

    return object_cols


