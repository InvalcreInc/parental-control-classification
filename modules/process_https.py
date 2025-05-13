from tld import get_tld

import pandas as pd
import sys
import os
from tqdm import tqdm
import logging
from multiprocessing import Pool
from extract_url_components import check_https, check_redirect
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_https_data(input_csv: str, output_csv: str, chunk_size: int = 100) -> None:
    """
    Read raw CSV (url, type, domain_age and domain_status), add is_https and has_redirect , and write to new CSV.
    """
    # Validate input CSV
    try:
        df_chunk = pd.read_csv(input_csv, nrows=1)
        if not {'url', 'type'}.issubset(df_chunk.columns):
            raise ValueError("Input CSV must have 'url' and 'type' columns")
    except Exception as e:
        logging.error(f"Failed to read {input_csv}: {str(e)}")
        raise

    # Process CSV in chunks
    chunks = pd.read_csv(input_csv)

    for i in tqdm(range(0, chunks.shape[0], chunk_size), colour="green", desc="Processing chunks"):
        chunk = chunks.iloc[i:i+chunk_size]
        df = process_chunks(chunk)
        df.to_csv(f"../data/{output_csv}", index=False, mode="a", header=False)
    logging.info(f"Successfully wrote output to {output_csv}")


def process_chunks(df: pd.DataFrame) -> pd.DataFrame:
    columns = ["url", "type",  "domain_age", "domain_status", "is_https"]
    final_df = pd.DataFrame(columns=columns)
    with Pool(processes=6) as pool:
        data = pool.map(process_row, df.iterrows())
        pool.close()
        pool.join()

    for i, row in enumerate(df.iterrows()):
        url = row[1]['url']
        row_type = row[1]['type']
        domain_age = row[1]["domain_age"]
        domain_status = row[1]["domain_status"]
        is_https = data[i]
        # Add row to chunk DataFrame
        final_df.loc[i] = [url, row_type, domain_age, domain_status, is_https]
    return final_df


def process_row(row) -> bool:
    url = row[1]['url']
    is_https = check_https(url)
    return is_https


if __name__ == "__main__":
    process_https_data('../data/mp_malicious_normalised.csv',
                       'phish_with_domain_https.csv')
