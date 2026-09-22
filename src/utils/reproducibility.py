# Primera función 
import pathlib


def load_config(file_path):
    """
    Load configuration from a YAML file.

    Args:
        file_path (str): Path to the YAML configuration file."""  

    pathlib.Path(__file__)

def set_seed(seed):
    """
    Set the random seed for reproducibility.

    Args:
        seed (int): The seed value to set.
    """
    import random
    import numpy as np
    import sklearn
    import lightgbm

    random.seed(seed)
    np.random.seed(seed)
    sklearn.utils.random.seed(seed)
    lightgbm.random_seed(seed)

def get_run_fingerprint(spark, tables):
    """
    Generate a fingerprint for the current run based on the Spark session and input tables.

    Args:
        spark (SparkSession): The Spark session object.
        tables (list): List of input tables used in the run.

    Returns:
        str: A unique fingerprint string for the current run.
    """
    import hashlib

    # Create a unique string based on the Spark session and input tables
    fingerprint_str = f"{spark.version}_{'_'.join(sorted(tables))}"
    
    # Generate a hash of the fingerprint string
    fingerprint_hash = hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    return fingerprint_hash
    