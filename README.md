# python-lambdas

A repository to house my generic python lambdas.


## Directory Structure

```plaintext
python-lambdas/
├── README.md
├── requirements.txt
├── .gitignore
├── lambdas/
│   ├── lambda1/
│   │   ├── __init__.py
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── lambda2/
│   │   ├── __init__.py
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── ...
├── tests/
│   ├── test_lambda1.py
│   ├── test_lambda2.py
│   └── ...
└── scripts/
    ├── deploy.sh
    └── build.sh
```

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/ocrosby/python-lambdas.git
    cd python-lambdas
    ``` 

2. Create a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

3. Upgrade pip
    ```sh
    pip install --upgrade pip
    ```
  
4. Install the project dependencies:
    ```sh
    pip install invoke
    pip install .
    ```


## Build Tasks

Since I am utilizing invoke to manage the build tasks, you can run the following commands to see the available tasks:

```sh
inv -l
```

### Build

To build the lambdas, run the following command:

```sh
inv build
```

### Deploy

To deploy the lambdas, run the following command:

```sh
inv deploy
```

### Test

To run the tests, run the following command:

```sh
inv test
```

### Clean

To clean the build artifacts, run the following command:

```sh
inv clean
```

### Syntax Analysis

To run the syntax analysis, run the following command:

```sh
inv lint
```


## References

- [Invoke](https://www.pyinvoke.org/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Pytest](https://docs.pytest.org/en/stable/)