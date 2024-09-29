import json
import datetime
import time
import http.client
from urllib.parse import urlparse
import boto3

def generate_url(gender: str, division: str, target_date: datetime.date) -> str:
    """
    Generate a URL for the specified date

    :param gender: Gender (male, female)
    :param division: Division (d1, d2, d3)
    :param target_date: Target date

    :return: URL
    """
    if gender is None or target_date is None or division is None:
        raise ValueError("Gender, target date, and division must be specified")

    gender = gender.strip().lower()
    if gender not in ['male', 'female']:
        raise ValueError(f"Invalid gender specified: expected '(male|female)' got '{gender}'!")

    gender_string = 'men' if gender == 'male' else 'women'

    division = division.strip().lower()
    if division not in ['d1', 'd2', 'd3']:
        raise ValueError(f"Invalid division specified: expected '(d1|d2|d3)' got '{division}'!")

    base_url = "https://data.ncaa.com/casablanca/scoreboard/soccer"
    formatted_date = target_date.strftime("%Y/%m/%d")
    return f"{base_url}-{gender_string}/{division}/{formatted_date}/scoreboard.json"

def fetch_matches(target_url: str):
    """
    Fetch the matches from the specified URL using http.client

    :param target_url: URL to fetch the matches
    :return: List of matches
    """
    parsed_url = urlparse(target_url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    conn.request("GET", parsed_url.path)
    response = conn.getresponse()

    if response.status != 200:
        print(f"Failed to fetch data from {target_url}: {response.status} {response.reason}")
        return []

    data = json.loads(response.read().decode())
    games = data.get('games', [])
    if len(games) == 0:
        return []

    updated_at = data.get('updated_at')
    updated_at = int(time.mktime(time.strptime(updated_at, "%m-%d-%Y %H:%M:%S")))

    fetched_matches = []
    for item in games:
        game = item.get('game')
        if game is None:
            continue

        match_data = extract_match_data(game, updated_at)
        if match_data:
            fetched_matches.append(match_data)

    return fetched_matches

def extract_match_data(game: dict, updated_at: int):
    """
    Extract the game data

    :param game: Game data
    :param updated_at: Updated at
    :return: important match data
    """
    home = game.get('home')
    away = game.get('away')

    if home is None or away is None:
        return None

    home_names = home.get('names')
    away_names = away.get('names')

    if home_names is None or away_names is None:
        return None

    home_full = home_names.get('full')
    away_full = away_names.get('full')

    home_score = home.get('score')
    away_score = away.get('score')

    home_conference = away_conference = None

    home_conferences = home.get('conferences')
    if home_conferences and isinstance(home_conferences, list) and home_conferences:
        home_conference = home_conferences[0].get('conferenceName')

    away_conferences = away.get('conferences')
    if away_conferences and isinstance(away_conferences, list) and away_conferences:
        away_conference = away_conferences[0].get('conferenceName')

    return {
        'id': int(game.get('gameID')),
        'processTimeEpoch': int(time.time()),
        'startTimeEpoch': int(game.get('startTimeEpoch')),
        'matchState': game.get('gameState'),
        'updatedAt': updated_at,
        'awayTeam': away_full,
        'awayScore': away_score,
        'awayConference': away_conference,
        'homeTeam': home_full,
        'homeScore': home_score,
        'homeConference': home_conference,
    }

def lambda_handler(event, context):
    """
    Lambda function to generate URL and fetch matches

    :param event: Lambda event
    :param context: Lambda context
    :return: List of matches
    """
    try:
        gender = event['gender']
        division = event['division']
        target_date_str = event['target_date']
        target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()

        target_url = generate_url(gender, division, target_date)
        matches = fetch_matches(target_url)

        return {
            'statusCode': 200,
            'body': json.dumps(matches)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"An error occurred: {str(e)}")
        }

# Example event to use with this lambda
example_event = {
    "gender": "male",
    "division": "d1",
    "target_date": "2023-10-15"
}
