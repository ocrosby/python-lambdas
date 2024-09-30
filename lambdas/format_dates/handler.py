"""
This Lambda function receives a JSON event containing a State object with an EnteredTime attribute.
"""
import json
from datetime import datetime, timedelta


def lambda_handler(event, context):
    """
    This handler receives a JSON event containing a State object with an EnteredTime attribute.
    It returns a JSON object with two date strings: today and yesterday.

    :param event: The event object
    :param context: The context object
    :return: A JSON object with two date strings
    """
    print(f"Received event: {json.dumps(event)}")
    print(f"Received context: {context}")

    entered_time = datetime.strptime(event['State']['EnteredTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
    today = entered_time.strftime('%Y-%m-%d')
    yesterday = (entered_time - timedelta(days=1)).strftime('%Y-%m-%d')

    return {
        "today": today,
        "yesterday": yesterday
    }
