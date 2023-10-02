import torch
import pandas as pd
from pathlib import Path
from typing import  Union
from datasets import load_dataset
from utils.common import read_yaml
from datasets.arrow_dataset import Dataset
from transformers import AutoTokenizer, AutoModel
from transformers.models.bert.modeling_bert import BertModel
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
class ModelPipeline:
    """
        Class used for LLM feature extraction.

        Attributes
        ----------
        source_url : str
            Hugging face source url.

        model_url : str
            model url.

        Methods
        -------
        data_loading()
            Loads HuggingFace dataset.

        llm_loading()
            Loads model and tokenizer.

    """

    def __init__(self, source_url: str, model_url: str):
        self.source_url = source_url
        self.model_url = model_url
        
    def data_loading(self) -> Dataset:
        """   
            Loads HuggingFace dataset.
            
            Returns
            -------
            dataset : datasets.arrow_dataset.Dataset
                Hugging face dataset.

        """    
        dataset = load_dataset(self.source_url, 
                               split="train")
        
        return dataset       

    def llm_loading(self) -> Union[BertModel, BertTokenizerFast]:
        """   
            Loads model and tokenizer.
            
            Returns
            -------
            model, tokenizer:  Union[BertModel, BertTokenizerFast]
            LLM model and its tokenizer.
        
        """    
        model = AutoModel.from_pretrained(self.model_url)
        tokenizer = AutoTokenizer.from_pretrained(self.model_url)
        

        return model, tokenizer
    
    def llm_inference(self, 
                      dataset: Dataset, 
                      model: BertModel, 
                      tokenizer: BertTokenizerFast) -> list:
        """   
            Loads model and tokenizer.

            Parameters
            ----------
            dataset : datasets.arrow_dataset.Dataset
                Hugging face dataset.

            model :  BertModel
                LLM model 

            tokenizer : BertTokenizerFast
                LLM model tokenizer.
        
            Returns
            -------
            predicted_categories : list
                List with predicted categories.
        
        """    
        if torch.cuda.is_available(): # using gpu
            model.to('cuda')            
            predictions = []
            
            categories = {
                        0: "Food",
                        1: "Health, Beauty",
                        2: "Electronics, Computers",
                        3: "Home and Kitchen",
                        4: "Clothing",
                        5: "Sports",
                        6: "Office",
                        7: "Movies, Music",
                        8: "Books"     
                    }
            
            for i, example in enumerate(dataset):
                title = example["title"]

                # prompt
                prompt = f"Classify the following product title into its category:\n\n{title}\n\nCandidate categories: {list(categories.values())}."

                # inputs
                inputs = tokenizer(prompt, return_tensors="pt").to('cuda')  # Mova os inputs para a GPU
                
                # pooler_output
                with torch.no_grad():
                    model_outputs = model(**inputs)
                    pooler_output = model_outputs.pooler_output

                # custom classifier
                class CustomClassifier(torch.nn.Module):
                    """
                        Personalized classification class. 
                        Used for classifying product categories                  
                    
                    """
                    def __init__(self):
                        super(CustomClassifier, self).__init__()
                        self.num_classes = len(categories)
                        self.classifier = torch.nn.Linear(
                                                            model.config.hidden_size, self.num_classes
                                                            ).to('cuda')

                    def forward(self, pooled_output):
                        return self.classifier(pooled_output)
                
                classifier = CustomClassifier()
                outputs = classifier(pooler_output)

                predicted_class = torch.argmax(outputs, dim=1).item()              
                predictions.append(predicted_class)

                # predicted categories
                predicted_categories = [categories[index] for index in predictions]
                
                print(f"Observation {i + 1}/{len(dataset)} processed")
                return predicted_categories
            else:
                raise ValueError("GPU not available. Model is too large to run on CPU.")
            
    def export_results(self, 
                       predicted_categories: list, 
                       dataset: Dataset,
                       path_file: str) -> None:
        """   
            Concats results with original dataset and saves it to disk.

            Parameters
            ----------
            predicted_categories : list
                List with predicted categories.

            dataset : datasets.arrow_dataset.Dataset
                Original HuggingFace dataset. 

            path_file : str
                Path to save parquet file

            Returns
            -------
            None
        """    
        data = {"category": predicted_categories}
        df_category = pd.DataFrame(data)
        df_final = pd.concat([dataset, df_category],axis=1)

        df_final.to_parquet(f"{path_file}.parquet", 
                            index=False, 
                            compression="gzip")

        return None

if __name__ == "__main__":
    # Initial parameters
    CONFIG_FILE_PATH = Path("config/config.yaml")
    config_path = read_yaml(CONFIG_FILE_PATH)    

    model_url = config_path.llm_pipe.model_tokenizer_URL
    source_url = config_path.data_ingestion.source_URL
    save_path = config_path.data_ingestion.local_data_file
    
    # Instantiate pipeline 
    pipeline = ModelPipeline(source_url, model_url)

    # Data Loading
    dataset = pipeline.data_loading()

    # Model and Tokenizer Loading
    model, tokenizer = pipeline.llm_loading()

    # LLM Inference
    predicted_categories = pipeline.llm_inference(
                                                  dataset,
                                                  model,
                                                  tokenizer
                                                  ) 
    # Outputs
    path_file = "df_categories"
    pipeline.export_results(
                            predicted_categories,
                            dataset,
                            path_file
                            )










  


