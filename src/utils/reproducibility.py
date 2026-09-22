# Primera función 
from pathlib import Path
import yaml
import random
import numpy as np


# Raíz del repo: este archivo está en src/utils/, así que sube 2 niveles
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "conf" / "config.yaml"


def load_config(file_path = DEFAULT_CONFIG):
    """
    Load configuration from a YAML file.

    Args:
        file_path (str): Path to the YAML configuration file."""  

    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def set_seeds(seed):
    """
    Set the random seed for reproducibility.

    Args:
        seed (int): The seed value to set.
    """

    random.seed(seed)
    np.random.seed(seed)


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
    