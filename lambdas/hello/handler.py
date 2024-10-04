"""
This module contains a simple Lambda function that returns a generic message.
"""

def lambda_handler(event: any, context: any):
    """
    Sample Lambda function that returns 'Hello, World!'

    :param event: The event object
    :param context: The context object
    :return: A JSON object with 'Hello, World!' message
    """
    print(f"Event: {event}")
    print(f"Context {context}")

    message = 'Hello, World!'
    return {
        'statusCode': 200,
        'body': message
    }
