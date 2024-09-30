import boto3
import json
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ncaa_match_data')
sqs = boto3.client('sqs')

# Define the SQS queue URLs
INGESTION_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/194227249447/NCAA-Match-Injestion-Queue'
UPDATE_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/194227249447/NCAA-Match-Update-Queue'

def has_match_changed(existing_match, new_match, keys_to_validate):
    """
    Compare all fields of the existing match and the new match.

    :param existing_match: Dictionary representing the existing match
    :param new_match: Dictionary representing the new match
    :param keys_to_validate: List of keys to validate
    :return: Boolean indicating if any field has changed
    """
    for key in keys_to_validate:
        if key not in existing_match or existing_match[key] != new_match[key]:
            return True
    return False

KEYS_TO_VALIDATE = [
    'id',
    'startTimeEpoch',
    'matchState',
    'division',
    'gender',
    'awayTeam',
    'awayScore',
    'awayConference',
    'homeTeam',
    'homeScore',
    'homeConference'
]

def lambda_handler(event, context):
    print("Context:", context)

    records = event.get('Records', [])
    processed_count = 0

    for record in records:
        message_id = record.get("messageId")
        body = record.get("body")
        print(f"Processing message '{message_id}': {body}")

        try:
            # Process each SQS message
            message_body = json.loads(body)

            match = {
                'id': int(message_body['id']),
                'messageId': message_id,
                'processTimeEpoch': int(time.time()),
                'startTimeEpoch': int(message_body['startTimeEpoch']),
                'matchState': message_body['matchState'],
                'division': message_body['division'],
                'gender': message_body['gender'],
                'updatedAt': int(message_body['updatedAt']),
                'awayTeam': message_body['awayTeam'],
                'awayScore': message_body['awayScore'],
                'awayConference': message_body['awayConference'],
                'homeTeam': message_body['homeTeam'],
                'homeScore': message_body['homeScore'],
                'homeConference': message_body['homeConference'],
            }

            # Extract id and startTimeEpoch from the message body
            match_id = match.get('id')
            start_time_epoch = match.get('startTimeEpoch')

            # Fetch the existing item from DynamoDB
            try:
                response = table.get_item(
                    Key={
                        'id': match_id,
                        'startTimeEpoch': start_time_epoch
                    }
                )
                existing_item = response.get('Item')
            except table.meta.client.exceptions.ResourceNotFoundException:
                existing_item = None

            if existing_item:
                # Process the existing item
                print(f"Existing match found '{match_id}'")
                if has_match_changed(existing_item, match, KEYS_TO_VALIDATE):
                    print(f"Match has changed '{match_id}'")
                    processed_count += 1

                    # Send the match to the update queue
                    sqs.send_message(
                        QueueUrl=UPDATE_QUEUE_URL,
                        MessageBody=json.dumps(match)
                    )
                else:
                    print(f"Match has not changed '{match_id}'")
            else:
                # Handle the case where the item does not exist
                print(f"New match found '{match_id}'")
                sqs.send_message(
                    QueueUrl=INGESTION_QUEUE_URL,
                    MessageBody=json.dumps(match)
                )

        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            print(body)
        except Exception as e:
            print(f"Error processing record: {e}")
            print(body)

    return {
        'statusCode': 200,
        'body': json.dumps(f"Processed {processed_count} records")
    }
