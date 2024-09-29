def lambda_handler(event: any, context: any):
    """Sample Lambda function that returns 'Hello, World!'"""
    print(f"Event: {event}")
    print(f"Context {context}")

    message = 'Hello, World!'
    return {
        'statusCode': 200,
        'body': message
    }
