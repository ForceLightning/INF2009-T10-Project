# INF2009 Team 10 Project
[![tests](https://github.com/ForceLightning/INF2009-T10-Project/actions/workflows/tests.yml/badge.svg)](https://github.com/ForceLightning/INF2009-T10-Project/actions/workflows/tests.yml) [![documentation](https://github.com/ForceLightning/INF2009-T10-Project/actions/workflows/documentation.yml/badge.svg)](https://github.com/ForceLightning/INF2009-T10-Project/actions/workflows/documentation.yml) [![Works](https://forcelightning-cdn.sgp1.digitaloceanspaces.com/works_on_my_machine.svg)](https://github.com/nikku/works-on-my-machine)
# Requirements

# Requirements
Python >= 3.10

# Installation
Install the python module requirements with either of the following:

```shell
pip install -r requirements.txt
```

```shell
pipenv install -r requirements.txt
```

# Development
For development, install from the [developer requirements file](./requirements-dev.txt) after performing the above.

## Tests
Run the following to process the test suites:
```shell
PYTHONPATH=./src python -m tests.run_tests
```

# Usage
## Environment Variables
Configure a `.env` file based on `example.env`. Note that the `DEVICE_IDX` field needs to be altered for each edge device during deployment.

## Preprocessing
Ensure that the data folder is populated with the following format:
`./data/raw_data/<name>/wifi_signal_strength.csv`
`./data/raw_data/<name>/btoutput.txt`
`./data/raw_data/<name>/images/image_<timestamp>.jpg`
`./data/manual_counts.csv`: Crowd population count (only necessary if training a model)
where the `<name>` is the name of the person who collected the data.

[Optional] Open and run the Jupyter notebooks [1](./preprocessing.ipynb) [2](./experimenting.ipynb)

Run the following to obtain a `bbox_results.csv` file.
```shell
PYTHONPATH=./src python -m util.people_detection
```

## Training
Run
```shell
PYTHONPATH=./src python -m train_and_score
```

## Deployment
As in [Environment Variables](#environment-variables), ensure that `DEVICE_IDX`, `PUBLISHER_INTERVAL`, `BROKER_IP`, `TOPIC`, `CLIENT_RETRIEVAL_TOPIC`, `RETURN_IMAGE`, `TOTAL_DEVICES`, `TOP_N_APS`, and `UVICORN_HOST` are set appropriately in a `.env` file.

For demonstration purposes, set `USE_DEMO_DATA` to `True`.

For `pipenv` users, the `.env` file will be loaded automatically when running any commands in a `pipenv shell` and thus the `PYTHONPATH=./src` portions of the following sections can be omitted.

### Edge Devices
Another reminder to set `DEVICE_IDX` in the `.env` file.

Run
```shell
PYTHONPATH=./src python -m deployment.edge_publisher
```

### Fog Device
Run
```shell
PYTHONPATH=./src python -m deployment.fog_subscriber
```

### API Server
Run
```shell
PYTHONPATH=./src python -m deployment.api
```

# Contributing

# Licence
[BSD-3 Clause](LICENSE.txt)
