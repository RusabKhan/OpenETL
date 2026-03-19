def dataframe_details(df):
    """
    Generate a dictionary containing details about each column in the DataFrame.

    Parameters:
        df (DataFrame): The input DataFrame for which details are to be generated.

    Returns:
        dict: A dictionary where keys are column names and values are their data types.
    """
    details = {}
    for col in df.columns:
        dtype = df[col].dtype.name
        # Mapping Pandas data types to SQLAlchemy data types
        if dtype == 'float64':
            dtype = 'Float'
        elif dtype == 'int64':
            dtype = 'Integer'
        elif dtype == 'bool':
            dtype = 'Boolean'
        elif dtype == 'object':
            dtype = 'String'
        elif dtype == 'datetime64[ns]':
            dtype = 'DateTime'
        elif dtype == 'timedelta64[ns]':
            dtype = 'Interval'
        elif dtype == 'category':
            dtype = 'Enum'
        elif dtype == 'bytes':
            dtype = 'LargeBinary'
        elif dtype == 'unicode':
            dtype = 'UnicodeText'
        elif dtype == 'period':
            dtype = 'Interval'
        elif dtype == 'object':
            if df[col].apply(lambda x: isinstance(x, dict)).any():
                dtype = 'Dictionary'
            elif df[col].apply(lambda x: isinstance(x, list)).any():
                dtype = 'Array'
        else:
            dtype = 'String'
        details[col] = str(dtype)
    return details
