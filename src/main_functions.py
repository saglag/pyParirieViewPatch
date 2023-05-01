"""Main functions for ephys processing"""
from typing import Dict, Any

import pandas as pd



def import_ephys(file_name):
    recording = pd.read_table(file_name, sep=r',', skipinitialspace=True)
    print(recording.head())
    return recording

def list_recordings(parent_folder_name):
    





