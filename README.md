# Tokenization and Masking API

This project implements an API using **FastAPI** to manage data tokenization, detokenization, and masking policies. It integrates with **PostgreSQL** for relational data storage and **MongoDB** for storing tokenization and masking policies. The API supports operations such as creating tokenization and masking policies, tokenizing and detokenizing single or batch records, and applying masking rules.

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
  ```bash
  curl -X POST "http://localhost:8000/create-domain-table/" \
  -H "Content-Type: application/json" \
  -d '{
        "tokenisation_pname": "PayrollTk1",
        "domain_name":"Payroll",
        "fields": [
            {"field_name": "name", "field_type": "char", "field_length": 50},
            {"field_name": "department", "field_type": "char", "field_length": 5},
            {"field_name": "email", "field_type": "alphanumeric", "field_length": 30},
            {"field_name": "account_id", "field_type": "numeric", "field_length": 30}
        ]
    }'
  ```
- **Response**:
  ```json
  {
    "status": "Domain table PayrollTk1 created successfully",
    "tokenisation_policy_id": "6657794b5ce60aa2ee3fbeb9"
  }
  ```

### 2. Tokenize Single Record

- **Endpoint**: `/tokenise-Single-record/`
- **Method**: POST
- **Description**: Tokenizes a single record based on the tokenization policy.
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/tokenise-Single-record/" \
  -H "Content-Type: application/json" \
  -d '{
    "tokenisation_policy_id": "6657794b5ce60aa2ee3fbeb9",
    "fields": {
        "name": "Rayan",
        "department": "Crasta",
        "email": "rayan@gmail.com",
        "account_id": "123"
    }
  }'
  ```
- **Response**:
  ```json
  {
    "result": {
      "name": "a7127",
      "department": "69d1fc",
      "email": "59e29@e3125.domain",
      "account_id": "331"
    }
  }
  ```

### 3. Detokenize Single Record

- **Endpoint**: `/detokenise-Single-record/`
- **Method**: GET
- **Description**: Detokenizes a single record and returns the original value.
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/detokenise-Single-record/" \
  -H "Content-Type: application/json" \
  -d '{
    "tokenisation_policy_id": "6657794b5ce60aa2ee3fbeb9",
    "fields": {
        "name": "a7127",
        "department": "69d1fc",
        "email": "59e29@e3125.domain",
        "account_id": "331"
    }
  }'
  ```
- **Response**:
  ```json
  {
    "result": {
      "name": "Rayan",
      "department": "Crasta",
      "email": "rayan@gmail.com",
      "account_id": "123"
    }
  }
  ```

### 4. Create Masking Policy

- **Endpoint**: `/create-masking-policy/`
- **Method**: POST
- **Description**: Creates a new masking policy for sensitive data.
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/create-masking-policy/" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "Health",
    "masking_policy_name": "Masking1",
    "tokenisation_policy_id": "6658d7ce91b5255a4633cab9",
    "rules": [
      {
        "field_name" : "NInumber",
        "show_start": 0,
        "show_last": 3
      },
      {
        "field_name" : "Bankdetail",
        "show_start": 0,
        "show_last": 3
      }
    ]
  }'
  ```
- **Response**:
  ```json
  {
    "status": "Masking Policy Masking1 Created",
    "masking_policy_id": "6658dfa75b53d2a11c3a8017"
  }
  ```

### 5. Get Masked Record

Note: We get masked record instead of detokenised data. The tokenised data will be the input

- **Endpoint**: `/get-masked-record/`
- **Method**: GET
- **Description**: Applies masking to sensitive data and returns the masked version.
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/get-masked-record/" \
  -H "Content-Type: application/json" \
  -d '{
    "tokenisation_policy_id": "6658da025d15f094ed330f7d",
    "masking_policy_id": "6658dfa75b53d2a11c3a8017",
    "key_pass": "password",
    "fields": {
        "name": "30bef",
        "age": "4",
        "NInumber": "42620",
        "Bankdetail": "05620",
        "Ward": "24",
        "Floor": "4"
    }
  }'
  ```
- **Response**:
  ```json
  {
    "result": {
      "name": "30bef",
      "age": "4",
      "NInumber": "XXX20",
      "Bankdetail": "XXX20",
      "Ward": "24",
      "Floor": "4"
    }
  }
  ```

### 6. Batch Tokenize

- **Endpoint**: `/batch-tokenise/`
- **Method**: POST
- **Description**: Tokenizes multiple records in a single request.
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/batch-tokenise/" \
  -H "Content-Type: application/json" \
  -d '{
    "tokenisation_policy_id": "6659cdf99b1f81c048086972",
    "domain_key": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWoY1lDAtmRwcQtBuPtC8LH6R+\nJspyFNPCKGhgSbWDDW4MomXj39vl/ad8F9eNiN/WARk0zIifNljZ54RxHUnrPskY\nnRxKM3gDaJmVTz/dU3Y0mQbT8soQvA4cUM02Umuc8sUn/Ed5bBQybCq2azzQJqIN\nHl2dKI3PjyZgzodf4wIDAQAB\n-----END PUBLIC KEY-----\n",
    "fields": [
      {"name": "Rayan", "SSN" : "489368351", "Card" : "4929381332664296"},
      {"name":"Crasta", "SSN":"690055315", "Card":"4916481158148111"}
    ]
  }'
  ```
- **Response**:
  ```json
  {
    "result": [
      {
        "name": "30bef",
        "SSN": "590569814",
        "Card": "5101041221355240"
      },
      {
        "name": "4zefg",
        "SSN": "915121344",
        "Card": "1972555531391524"
      }
    ]
  }
  ```

### 7. Batch Detokenize

- **Endpoint**: `/batch-detokenise/`
- **Method**: GET
- **Description**: Detokenizes multiple records and returns their original values.
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/batch-detokenise/" \
  -H "Content-Type: application/json" \
  -d '{
    "tokenisation_policy_id": "6659cdf99b1f81c048086972",
    "key_pass": "supersecure",
    "fields": [
      {
        "name": "30bef",
        "SSN": "590569814",
        "Card": "5101041221355240"
      },
      {
        "name": "4zefg",
        "SSN": "915121344",
        "Card": "1972555531391524"
      }
    ]
  }'
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

