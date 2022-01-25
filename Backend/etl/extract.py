import pandas as pd


def extract_csv(path: str) -> pd.DataFrame:
    """
    Generates a pandas data frame out of a csv file, which is located under the given path.

    :param path: Path to the csv file
    :return: a pandas dataframe of the csv file
    """
    import os
    os.listdir()
    return pd.read_csv(path,  sep=';')
