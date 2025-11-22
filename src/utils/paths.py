# src/utils/paths.py
import os

def get_project_root():
    # src/utils/paths.py → src/utils → src → project root
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def get_data_path(filename):
    root = get_project_root()
    data_folder = os.path.join(root, "data")
    
    # Make sure folder exists
    os.makedirs(data_folder, exist_ok=True)

    return os.path.join(data_folder, filename)
