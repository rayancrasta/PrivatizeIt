import pandas as pd
import requests
import time
import os
import json

class APIClient:
    def __init__(self):
        pass
    
    def preprocess_data(self, csv_path):
        df = pd.read_csv(csv_path)
        df['SSN'] = df['SSN'].str.replace('-', '')
        df['Card'] = df['Card'].str.replace('-', '')

        df['Card'] = pd.to_numeric(df['Card'], errors='coerce')
        df = df.dropna(subset=['Card'])

        df['SSN'] = df['SSN'].astype(int)
        df['Card'] = df['Card'].astype(int)
        df['Name'] = df['Name'].astype(str)

        return df

    def tokenise_requests(self, df, api_url, rowsize, tokenisation_policy_id, domain_key):
        headers = {'Content-Type': 'application/json'}
        success = 0
        start_time = time.time()
        responses = [] #save data

        for index, row in df.head(rowsize).iterrows():
            payload = {
                "tokenisation_policy_id": tokenisation_policy_id,
                "domain_key": domain_key,
                "fields": {
                    "name": row['Name'],
                    "SSN": row['SSN'],
                    "Card": row['Card']
                }
            }

            response = requests.post(api_url, json=payload, headers=headers)

            if response.status_code == 200:
                success += 1
                responses.append(response.json()['result'])
            else:
                print(response.text)
        
        end_time = time.time()
        print("Tokenisation Successful requests:", success)
        print("Time taken:", end_time - start_time)

        return responses

    def create_df(self,responses):
        data = [(r['name'], r['SSN'], r['Card']) for r in responses]
        
        tokenised_df = pd.DataFrame(data, columns=['Name', 'SSN', 'Card'])
        return tokenised_df

    def detokenise_requests(self, df, api_url, tokenisation_policy_id, key_pass):
        headers = {'Content-Type': 'application/json'}
        success = 0
        start_time = time.time()
        responses = [] #save data

        for index, row in df.iterrows():
            payload = {
                "tokenisation_policy_id": tokenisation_policy_id,
                "key_pass": key_pass,
                "fields": {
                    "name": row['Name'],
                    "SSN": row['SSN'],
                    "Card": row['Card']
                }
            }

            response = requests.get(api_url, json=payload, headers=headers)

            if response.status_code == 200:
                success += 1
                responses.append(response.json()['result'])
            else:
                print(response.text)
        
        end_time = time.time()
        print("Detokenisation Successful requests:", success)
        print("Time taken:", end_time - start_time)
        
        return responses

def main():
    csv_path = os.path.join('data', 'card_data.csv')
    t_api_url = "http://localhost:8000/tokenise-Single-record"
    tokenisation_policy_id = "6659cdf99b1f81c048086972"
    domain_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWoY1lDAtmRwcQtBuPtC8LH6R+\nJspyFNPCKGhgSbWDDW4MomXj39vl/ad8F9eNiN/WARk0zIifNljZ54RxHUnrPskY\nnRxKM3gDaJmVTz/dU3Y0mQbT8soQvA4cUM02Umuc8sUn/Ed5bBQybCq2azzQJqIN\nHl2dKI3PjyZgzodf4wIDAQAB\n-----END PUBLIC KEY-----\n"
    
    rowsize = 100
    client = APIClient()
    df = client.preprocess_data(csv_path)
    responses = client.tokenise_requests(df, t_api_url, rowsize,tokenisation_policy_id, domain_key)
    # print(responses)
    tokenised_df = client.create_df(responses)
    
    dt_api_url = "http://localhost:8000/detokenise-Single-record"
    key_pass = "supersecure"
    responses = client.detokenise_requests(tokenised_df, dt_api_url, tokenisation_policy_id, key_pass)
    original_df = client.create_df(responses)
    
    if (df.head(rowsize)).equals(original_df):
        print("The DataFrames are identical.")
    else:
        print("The DataFrames are different.")    

    print(df.head(rowsize))
    print(original_df)
    
if __name__ == "__main__":
    main()
