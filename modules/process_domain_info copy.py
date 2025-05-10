

from tld import get_tld

import pandas as pd
import sys
import os
from tqdm import tqdm
import logging
import urllib
from multiprocessing import Pool
sys.path.append(os.path.abspath(os.path.join('..')))
from modules.fetch_domain_info import get_domain_info
domains: dict[str, dict[str, int]] = {}


def process_whois_data(input_csv: str, output_csv: str, chunk_size: int = 10000) -> None:
    """
    Read raw CSV (url, type), add domain_age and domain_status, and write to new CSV.
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
    domains: dict[str, dict[str, int]] = {}
    chunks = pd.read_csv(input_csv)
    rows = chunks.iterrows()

    for i in tqdm(range(0, chunks.shape[0], chunk_size), colour="green", desc="Processing chunks"):
        chunk = chunks.iloc[i:i+chunk_size]
        df = process_chunks(chunk)
        df.to_csv(f"../data/{output_csv}", index=False, mode="a")

    #
    columns = ["url", "type",  "domain_age", "domain_status"]
    final_df = pd.DataFrame(columns=columns)
    for i, row in tqdm(rows, total=chunks.shape[0], colour="green", desc="Processing chunks"):
        try:
            url = row['url']
            url_type = row['type']
            domain = get_domain(url)
            if not domain or not url_type:
                raise ValueError("Invalid domain")

            with Pool(processes=4) as pool:
                domain_info = pool.map

            if domain not in domains:
                if pd.isna(url_type) or url_type != "benign":
                    domains[domain] = {
                        "domain_age": 0,
                        "domain_status": 0
                    }
                else:
                    domains[domain] = get_domain_info(url)

            domain_info = domains[domain]
            domain_age = domain_info["domain_age"]
            domain_status = domain_info["domain_status"]
            logging.info(
                f'Processed row {i}: {domain} {url_type} {domain_age} {domain_status}')

            # Add row to chunk DataFrame
            final_df.loc[i] = [url, url_type, domain_age,
                               domain_status]
        except Exception as e:
            logging.error(f"Failed to process row {i}: {str(e)}")
            continue
    final_df.to_csv(f"../data/{output_csv}", index=False, mode="a")
    logging.info(f"Successfully wrote output to {output_csv}")


def process_chunks(df: pd.DataFrame) -> pd.DataFrame:
    columns = ["url", "type",  "domain_age", "domain_status"]
    final_df = pd.DataFrame(columns=columns)
    with Pool(processes=4) as pool:
        domain_info = pool.map(process_row, df.iterrows())
        pool.close()
        pool.join()

    for i, row in enumerate(df.iterrows()):
        url = row[1]['url']
        row_type = row[1]['type']
        domain_age = domain_info[i]["domain_age"]
        domain_status = domain_info[i]["domain_status"]
        # Add row to chunk DataFrame
        final_df.loc[i] = [url, row_type, domain_age,
                           domain_status]
    return final_df


def process_row(row: pd.Series) -> dict[str, int]:
    try:
        url = row['url']
        url_type = row['type']
        domain = get_domain(url)
        if not domain or not url_type:
            raise ValueError("Invalid domain")
        if domain not in domains:
            if pd.isna(url_type) or url_type != "benign":
                domains[domain] = {
                    "domain_age": 0,
                    "domain_status": 0
                }
            else:
                domains[domain] = get_domain_info(url)
        return domains[domain]
    except:
        pass
    return {
        'domain_age': 0,
        'domain_status': 0
    }


def get_domain(url: str):
    try:
        res = get_tld(url, fail_silently=True,
                      fix_protocol=True, as_object=True)
        parsed_url = res.parsed_url
        return parsed_url.netloc
    except:
        return None


if __name__ == '__main__':
    process_whois_data('../data/malicious_phish.csv',
                       'malicious_phish_domain.csv')
