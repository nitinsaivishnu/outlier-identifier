from fastapi import FastAPI, Path, HTTPException
from enum import Enum
from utils.utils import get_random_30_points,detect_outliers_zscore
import numpy as np
import pandas as pd
import os,json,glob,random



app = FastAPI()

class Exchange(str, Enum):
    nasdaq = "NASDAQ"
    lse = "LSE"
    nyse= "NYSE"

@app.get("/")
async def root():
    return {"message": "Server up and running"}

def select_files(directory, num_files):
    """
    Selects up to `num_files` files from the specified `directory`.
    If the directory contains fewer files than `num_files`, all files are selected.

    Parameters:
        directory (str): The path to the directory.
        num_files (int): The number of files to select.

    Returns:
        list: A list of selected file paths.
    """
    try:
        files = os.listdir(directory)
        if not files:
            raise HTTPException(status_code=404, detail="No files found in the directory")
        files=glob.glob(f"{directory}/*.csv")
        num_files_in_dir = len(files)
        num_files_to_select = min(num_files_in_dir, num_files)
        selected_files = random.sample(files, num_files_to_select)
        return selected_files
    except FileNotFoundError as ex:
        raise HTTPException(status_code=404, detail=f"Error {ex} Directory not found: {directory}")

def format_number(number):
    try:
        return round(number,2)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Failed with error {ex}")


@app.post("/stock_exchange/{exchange_name}/input/{input_value}/threshold/{threshold}")
async def outlier(exchange_name:Exchange = Path(..., description="This parameter must be one of below values"),input_value: int = Path(..., description="This parameter must be either 1 or 2"),threshold:int =Path(..., description="Deviation parameter")):
    
    """
    Endpoint to select Stock Exchange and no.of input files to understand outliers with a given threshold.

    Parameters:
        exchange_name (str): Name of the exchange.
        input_value (int): The number of files to select (between 1 and 2).
        threshold(int): Standard deviation threshold

    Returns:
        dict: Success when files are outlier created .
    """
    
    print(exchange_name,input_value)
    if input_value not in [1, 2]:
        raise HTTPException(status_code=400, detail="Input value must be 1 or 2")
    
    if exchange_name not in Exchange.__members__.values():
        raise HTTPException(status_code=400, detail="Enum parameter must be one of 'LSE' or 'NASDAQ' or 'NYSE'")
    
    exchange_path=f"data/{exchange_name}"
    
    selected_files = select_files(exchange_path, input_value)
    print(selected_files)
    try:
        for file in selected_files:
            df = pd.read_csv(file,names=["Stock-ID", "Timestamp", "price"])
            if df.empty:
                raise HTTPException(status_code=400, detail=f"CSV file is empty: {file}")
            stock_id = df["Stock-ID"][0]
            random_30_points = get_random_30_points(df)
            prices = random_30_points['price'].values
            outliers = detect_outliers_zscore(prices)

            mean_price = np.mean(prices)
            threshold = threshold  # Threshold for % deviation over and above

            result_data = []
            for outlier_idx in outliers:
                timestamp = random_30_points.iloc[outlier_idx]['Timestamp']
                actual_price = prices[outlier_idx]
                deviation = actual_price - mean_price
                percentage_deviation = (deviation / mean_price) * 100

                if np.abs(percentage_deviation) > threshold:
                    result_data.append({
                        'Stock-ID': stock_id,
                        'Timestamp': timestamp,
                        'Actual Price': format_number(actual_price),
                        'Mean Price': format_number(mean_price),
                        'Deviation': format_number(deviation),
                        '% Deviation': format_number(percentage_deviation)
                    })
            result_df=''
            if result_data:
                result_df = pd.DataFrame(result_data)
                result_filename = f'results_{exchange_name}_{stock_id}.csv'
                if not os.path.exists('results'):
                    os.makedirs('results')
                result_filepath = os.path.join('results', result_filename)
                result_df.to_csv(result_filepath, index=False)
            else:
                raise HTTPException(status_code=400, detail=f"No outliers found for specified threshold {threshold} . try decreasing it")
            res = result_df.to_json(orient="records")
            parsed = json.loads(res)
            print(parsed)
        return {"exchange_name": exchange_name,"status":"Outlier file/files created successfully inside results folder "}
    
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail=f"CSV file has an invalid format")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Failed due to exception {ex}")
