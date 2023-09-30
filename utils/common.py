from box import ConfigBox
from box.exceptions import BoxValueError
from pathlib import Path
import yaml

def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """       
        Reads yaml file

        Parameters
        ----------
        path_to_yaml : str
        yaml file path

        Raises
        -------
        ValueError: if yaml empty
        e: empty file

        Returns
        -------
        ConfigBox: ConfigBox type 
    
    """

    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("O yaml está vazio")
    except Exception as e:
        raise e
    
