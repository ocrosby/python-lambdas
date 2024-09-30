"""
This file contains the test cases for the hello lambda function.
"""

import pytest
from lambdas.hello.handler import lambda_handler

# Define test cases
test_cases = [
    {
        "name": "Basic Hello World",
        "event": {},
        "context": {},
        "expected": {
            "statusCode": 200,
            "body": "Hello, World!"
        }
    },
    # Add more test cases here if needed
]

@pytest.mark.parametrize("test_case", test_cases, ids=[tc["name"] for tc in test_cases])
def test_lambda_handler(test_case):
    """
    Test the hello lambda_handler function

    :param test_case:
    :return:
    """
    # Arrange
    event = test_case.get("event")
    context = test_case.get("context")

    # Act
    response = lambda_handler(event, context)

    # Assert
    assert response == test_case["expected"]
