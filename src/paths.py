import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Define directories
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
DATA_DIR = os.path.join(ROOT_DIR, "data")
INPUTS_DIR = os.path.join(DATA_DIR, "inputs")
OUTPUTS_DIR = os.path.join(DATA_DIR, "outputs")
