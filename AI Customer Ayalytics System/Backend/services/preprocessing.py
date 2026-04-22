import pandas as pd

def clean_csv_data(file_path: str) -> pd.DataFrame:
    # Load the uploaded CSV file
    df = pd.read_csv(file_path)
    
    # Remove duplicate records
    df = df.drop_duplicates()
    
    # Handle missing values (e.g., fill or drop)
    df = df.dropna()
    
    # Return the cleaned dataframe for ML processing
    return df