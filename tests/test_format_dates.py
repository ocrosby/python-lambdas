"""
This module contains the test cases for the format_dates function.
"""

import pytest
from lambdas.format_dates.handler import lambda_handler  # Adjust the import based on your module structure

# Define test cases
test_cases = [
    {
        "event": {
            "State": {
                "EnteredTime": "2023-10-15T12:34:56.789Z"
            }
        },
        "context": {},
        "expected": {
            "today": "2023-10-15",
            "yesterday": "2023-10-14"
        }
    },
    {
        "event": {
            "State": {
                "EnteredTime": "2023-01-01T00:00:00.000Z"
            }
        },
        "context": {},
        "expected": {
            "today": "2023-01-01",
            "yesterday": "2022-12-31"
        }
    },
    # Add more test cases as needed
]


@pytest.mark.parametrize("test_case", test_cases)
def test_format_dates(test_case):
    """
    Test the format_dates lambda function.

    :param test_case:
    :return:
    """
    # Arrange
    event = test_case["event"]
    context = test_case["context"]
    expected_output = test_case["expected"]

    # Act
    result = lambda_handler(event, context)

    # Assert
    assert result == expected_output, f"Expected: {expected_output}, but got: {result}"
