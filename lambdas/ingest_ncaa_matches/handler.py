import json
import boto3
from botocore.exceptions import ClientError

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = 'ncaa_match_data'  # Replace with your DynamoDB table name
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Lambda function to read match data from the event and insert it into DynamoDB.
    """
    try:
        # Parse the match data from the event
        match_data = json.loads(event['Records'][0]['body'])

        # Insert the match data into DynamoDB
        response = table.put_item(Item=match_data)
        print(f"DynamoDB response: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps('Match data inserted successfully!')
        }
    except ClientError as e:
        print(f"ClientError: {e.response['Error']['Message']}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inserting data into DynamoDB: {e.response['Error']['Message']}")
        }
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"An error occurred: {str(e)}")
        }