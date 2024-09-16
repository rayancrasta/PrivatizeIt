# Tokenization and Masking API

This project implements an API using **FastAPI** to manage data tokenization, detokenization, and masking policies. It integrates with **PostgreSQL** for relational data storage and **MongoDB** for storing tokenization and masking policies. The API supports operations such as creating tokenization and masking policies, tokenizing and detokenizing single or batch records, and applying masking rules.

## Concepts
**Tokenization** replaces sensitive data with non-sensitive tokens that look similar but have no real value. For example, "1234-5678-9876-5432" might be tokenized to "XXXX-XXXX-XXXX-5432".

**Masking** hides parts of data while keeping some visible. For instance, "1234-5678-9876-5432" might be masked to "1234-XXXX-XXXX-5432" to show only the last four digits

## Features

1. **Tokenization Policies**: Create and manage tokenization policies. These policies are stored in both PostgreSQL and MongoDB.
2. **Masking Policies**: Define and apply masking rules to sensitive data.
3. **Data Encryption**: Uses RSA encryption to secure sensitive data.
4. **Batch Processing**: Tokenize and detokenize records in batches for efficiency.
5. **Asynchronous Operations**: All database interactions are handled asynchronously for optimal performance.

## API Endpoints

### 1. Create Tokenization Policy

- **Endpoint**: `/create-domain-table/`
- **Method**: POST
- **Description**: Creates a new tokenization policy in both PostgreSQL and MongoDB.
- **Example**:
- **Request**:
  ```json
    {
        "tokenisation_pname": "CardTk1",
        "domain_name": "Card",
        "key_pass": "supersecure",
        "fields": [
            {
                "field_name": "SSN",
                "field_type": "numeric",
                "field_length": 9
            },
            {
                "field_name": "Card",
                "field_type": "numeric",
                "field_length": 16
            }
        ]
    }
  ```
- **Response**:
  ```json
  {
    "status": "Domain table CardTk1 created successfully",
    "tokenisation_policy_id": "6659cdf99b1f81c048086972"
  }
  ```

### 2. Tokenize Single Record

- **Endpoint**: `/tokenise-Single-record/`
- **Method**: POST
- **Description**: Tokenizes a single record based on the tokenization policy.
- **Example**:
- **Request**:
  ```json
    {
        "tokenisation_policy_id": "6659cdf99b1f81c048086972",
        "domain_key": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWoY1lDAtmRwcQtBuPtC8LH6R+\nJspyFNPCKGhgSbWDDW4MomXj39vl/ad8F9eNiN/WARk0zIifNljZ54RxHUnrPskY\nnRxKM3gDaJmVTz/dU3Y0mQbT8soQvA4cUM02Umuc8sUn/Ed5bBQybCq2azzQJqIN\nHl2dKI3PjyZgzodf4wIDAQAB\n-----END PUBLIC KEY-----\n",
        "fields": {
            "name": "Rayan",
            "SSN" : "489368351",
            "Card" : "4929381332664296"
        }
    }
  ```
- **Response**:
  ```json
    {
        "result": {
            "name": "Rayan",
            "SSN": "112536168",
            "Card": "3324779219528551"
        }
    }
  ```

### 3. Detokenize Single Record

- **Endpoint**: `/detokenise-Single-record/`
- **Method**: GET
- **Description**: Detokenizes a single record and returns the original value.
- **Example**:
- **Request**:
  ```json
    {
        "tokenisation_policy_id": "6659cdf99b1f81c048086972",
        "key_pass":"supersecure",
        "fields": {
            "name": "Rayan",
            "SSN": "003309024",
            "Card": "7018575315830004"
        }
    }
  ```
- **Response**:
  ```json
    {
        "result": {
            "name": "Rayan",
            "SSN": "489368351",
            "Card": "4929381332664296"
        }
    }
  ```

### 4. Create Masking Policy

- **Endpoint**: `/create-masking-policy/`
- **Method**: POST
- **Description**: Creates a new masking policy for sensitive data.
- **Example**:
- **Request**:
  ```json
    {
        "domain_name": "Card",
        "masking_policy_name":"CardMsk2",
        "tokenisation_policy_id": "6659cdf99b1f81c048086972",
        "rules": [
            {
                "field_name" : "SSN",
                "show_start": 0,
                "show_last": 3
            },
            {
                "field_name" : "Card",
                "show_start": 0,
                "show_last": 4
            }
        ]
    }
  ```
- **Response**:
  ```json
    {
        "status": "Masking Policy CardMsk2 Was Created",
        "masking_policy_id": "66e8a127174190cfd4a06cc1"
    }
  ```

### 5. Get Masked Record

Note: We get masked record instead of detokenised data. The tokenised data will be the input

- **Endpoint**: `/get-masked-record/`
- **Method**: GET
- **Description**: Applies masking to sensitive data and returns the masked version.
- **Example**:
- **Request**:
  ```json
    {
        "tokenisation_policy_id": "6659cdf99b1f81c048086972",
        "masking_policy_id": "6659ce579b1f81c048086973",
        "key_pass":"supersecure",
        "fields": {
            "name": "Rayan",
            "SSN": "003309024",
            "Card": "7018575315830004"
        }
    }
  ```
- **Response**:
  ```json
    {
        "result": {
            "name": "Rayan",
            "SSN": "XXXXXX351",
            "Card": "XXXXXXXXXXXX4296"
        }
    }
  ```

### 6. Batch Tokenize

- **Endpoint**: `/batch-tokenise/`
- **Method**: POST
- **Description**: Tokenizes multiple records in a single request.
- **Example**:
- **Request**:
  ```json
    {
        "tokenisation_policy_id": "6659cdf99b1f81c048086972",
        "domain_key": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWoY1lDAtmRwcQtBuPtC8LH6R+\nJspyFNPCKGhgSbWDDW4MomXj39vl/ad8F9eNiN/WARk0zIifNljZ54RxHUnrPskY\nnRxKM3gDaJmVTz/dU3Y0mQbT8soQvA4cUM02Umuc8sUn/Ed5bBQybCq2azzQJqIN\nHl2dKI3PjyZgzodf4wIDAQAB\n-----END PUBLIC KEY-----\n",
        "fields": [{"name": "Rayan","SSN" : "489368351","Card" : "4929381332664296"},
        {"name":"Crasta","SSN":"690055315","Card":"4916481158148111"}]
    }
  ```
- **Response**:
  ```json
    {
        "result": [
            {
                "name": "Rayan",
                "SSN": "702752454",
                "Card": "3123801124762593"
            },
            {
                "name": "Crasta",
                "SSN": "710393394",
                "Card": "0119404503031834"
            }
        ]
    }
  ```

### 7. Batch Detokenize

- **Endpoint**: `/batch-detokenise/`
- **Method**: GET
- **Description**: Detokenizes multiple records and returns their original values.
- **Example**:

- **Request**:
  ```json
    {
        "tokenisation_policy_id": "6659cdf99b1f81c048086972",
        "key_pass":"supersecure",
        "fields": [
            {
                "name": "Rayan",
                "SSN": "702752454",
                "Card": "3123801124762593"
            },
            {
                "name": "Crasta",
                "SSN": "710393394",
                "Card": "0119404503031834"
            }
        ]
    }
  ```
- **Response**:
  ```json
  {
    "result": [
      {
        "name": "Rayan",
        "SSN": "489368351",
        "Card": "4929381332664296"
      },
      {
        "name": "Crasta",
        "SSN": "690055315",
        "Card": "4916481158148111"
      }
    ]
  }
  ```

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your PostgreSQL and MongoDB instances and update the connection strings in `database.py` and `mongodb.py`.

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

