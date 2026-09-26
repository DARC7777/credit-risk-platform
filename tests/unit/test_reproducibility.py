import numpy as np
from src.utils.reproducibility import set_seeds
import random

def test_set_seeds_same_result():
    set_seeds(42)
    result1 = np.random.rand(5)
    
    set_seeds(42)
    result2 = np.random.rand(5)
    
    assert np.array_equal(result1, result2)

def test_set_seeds_different_result():
    set_seeds(42)
    result1 = np.random.rand(5)
    
    set_seeds(43)
    result2 = np.random.rand(5)
    
    assert not np.array_equal(result1, result2)

def test_set_seeds_reproducibility():

    set_seeds(42)
    result1 = random.random()

    set_seeds(42)
    result2 = random.random()

    assert result1 == result2