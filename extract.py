from datasets import load_dataset
from pathlib import Path
from utils.common import read_yaml

def data_ingestion(source_url: str, save_path: str) -> None:
    """   
        Reads HuggingFace data and saves it to disk.

        Parameters
        ----------
        source_url : str
        Hugging face source url.

        save_path: str
        Desired local path.
        
        Returns
        -------
        None 
    
    """    
    dataset = load_dataset(source_url, 
                           split="train")
    
    dataset.save_to_disk(save_path)

    return None

if __name__ == "__main__":

    # Initial parameters
    CONFIG_FILE_PATH = Path("config/config.yaml")
    config_path = read_yaml(CONFIG_FILE_PATH)

    extract_config = config_path.data_ingestion
    source_url = extract_config.source_URL
    save_path = extract_config.local_data_file

    # Extracting data
    data_ingestion(source_url, save_path)

