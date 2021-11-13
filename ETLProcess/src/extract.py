import pandas as pd


def extract_csv(path: str) -> pd.DataFrame:
    """
    Generates a pandas data frame out of a csv file, which is located under the given path.
    :param path: Path to the csv file
    :return: a pandas dataframe of the csv file
    """
    return pd.read_csv(path,  sep=';')


def extract_all(paths: [str]) -> [pd.DataFrame]:
    """
    Generates a pandas data frame out of a csv file for each of the given paths.
    :param paths: List of Paths to csv files
    :return: a list of pandas dataframes corresponding to the different csv files.
    """
    dfs = list()
    for path in paths:
        dfs.append(extract_csv(path))
    return dfs
