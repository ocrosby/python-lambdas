import pytest
from lambdas.hello.handler import lambda_handler

# Define test cases
test_cases = [
    {
        "name": "Basic Hello World",
        "input": {},
        "expected": {
            "statusCode": 200,
            "body": "Hello, World!"
        }
    },
    # Add more test cases here if needed
]

@pytest.mark.parametrize("test_case", test_cases, ids=[tc["name"] for tc in test_cases])
def test_lambda_handler(test_case):
    response = lambda_handler(test_case["input"], None)
    assert response == test_case["expected"]
