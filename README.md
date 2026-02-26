## Introduction

This program implements the client part (which is run by each data provider) of the INDICATE data exchange protocol.

## Requirements.

* Python >= 3.10

* Access to the INDICATE Data Exchange API

## Installation

To install the dependencies of the data exchange client, please execute the following from the root directory:

```bash
pip3 install -r requirements.txt
```

## Usage

When not running inside a container, create a `.env` file with options

```
DATABASE_HOST=database-host
DATABASE_PORT=1234
DATABASE_USER=user
DATABASE_PASSWORD=password
DATABASE_NAME=name

PROVIDER_ID_FILE=47d3832d-1343-11f1-abf6-ac91a15cb2bb
DATA_EXCHANGE_ENDPOINT=http://data-exchange:1234/

TRIGGER_ADDRESS=0.0.0.0
TRIGGER_PORT=1234
```

or set the corresponding environment variables. Then run the program with

```bash
PYTHONPATH=. python3 indicate_data_exchange_client/main.py
```

## Code Generation

The directory `openapi-generation` contains the OpenAPI definition of the data exchange protocol and the configuration for the code generator.
To regenerate the code of this program for a new version of the protocol

1. Copy the new OpenAPI definition to `openapi-generation/api.yaml`

2. Run `cd openapi-generation ; ./generate.sh`

3. Test the generated code

4. Commit all changes
