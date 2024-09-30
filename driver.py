import json
import time
import datetime

import boto3
import requests

from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/194227249447/NCAA-Match-Data-Queue'

# SQS Queue Information
# Name: NCAA-Match-Data-Queue

class URLIterator:
    """
    URL Iterator
    """
    def __init__(self, genders, divisions, start_date, end_date):
        """
        Initialize the URL iterator

        :param genders: a list of genders
        :param divisions: a list of divisions
        :param start_date: start date
        :param end_date: end date
        """
        self.genders = genders
        self.divisions = divisions
        self.current_date = start_date
        self.end_date = end_date
        self.gender_index = 0
        self.division_index = 0
        self.counter = 0

    def __iter__(self):
        """
        Return the iterator object

        :return: iterator object
        """
        return self

    def __next__(self):
        """
        Return the next URL

        :return: URL
        """
        if self.current_date > self.end_date:
            raise StopIteration

        gender = self.genders[self.gender_index]
        division = self.divisions[self.division_index]
        url = generate_url(gender, division, self.current_date)

        # Update indices for the next iteration
        self.division_index += 1
        if self.division_index >= len(self.divisions):
            self.division_index = 0
            self.gender_index += 1
            if self.gender_index >= len(self.genders):
                self.gender_index = 0
                self.current_date += datetime.timedelta(days=1)

        self.counter += 1
        return url

    def get_current_gender(self):
        """
        Get the current gender

        :return: Gender
        """
        return self.genders[self.gender_index]

    def get_current_division(self):
        """
        Get the current division

        :return: Division
        """
        return self.divisions[self.division_index]

    def get_counter(self):
        """
        Get the counter

        :return: Counter
        """
        return self.counter


def generate_url(gender: str, division: str, target_date: datetime.date) -> str:
    """
    Generate a URL for the specified date

    :param gender: Gender (male, female)
    :param division: Division (d1, d2, d3)
    :param target_date: Target date

    :return: URL
    """
    if gender is None:
        raise ValueError("The gender must be specified")

    if target_date is None:
        raise ValueError("The target date must be specified")

    if division is None:
        raise ValueError("The division must be specified")

    gender = gender.strip().lower()
    if len(gender) == 0:
        raise ValueError("Gender cannot be empty")

    if gender not in ['male', 'female']:
        raise ValueError(f"Invalid gender specified: expected '(male|female)' got '{gender}'!")

    if gender == 'male':
        gender_string = 'men'
    else:
        gender_string = 'women'

    division = division.strip().lower()
    if len(division) == 0:
        raise ValueError("Division cannot be empty")

    if division not in ['d1', 'd2', 'd3']:
        raise ValueError(f"Invalid division specified: expected '(d1|d2|d3)' got '{division}'!")

    base_url = "https://data.ncaa.com/casablanca/scoreboard/soccer"
    formatted_date = target_date.strftime("%Y/%m/%d")
    result = f"{base_url}-{gender_string}/{division}/{formatted_date}/scoreboard.json"

    return result


def extract_match_data(game: dict, active_gender: str, active_division: str, updated_at: int):
    """
    Extract the game data

    :param game: Game data
    :param active_gender: Gender
    :param active_division: Division
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
    if home_conferences is not None and isinstance(home_conferences, list) and len(home_conferences) > 0:
        home_conference = home_conferences[0].get('conferenceName')

    away_conferences = away.get('conferences')
    if away_conferences is not None and isinstance(away_conferences, list) and len(away_conferences) > 0:
        away_conference = away_conferences[0].get('conferenceName')

    return {
        'id': int(game.get('gameID')),
        'processTimeEpoch': int(time.time()),
        'startTimeEpoch': int(game.get('startTimeEpoch')),
        'matchState': game.get('gameState'),
        'division': active_division,
        'gender': active_gender,
        'updatedAt': updated_at,
        'awayTeam': away_full,
        'awayScore': away_score,
        'awayConference': away_conference,
        'homeTeam': home_full,
        'homeScore': home_score,
        'homeConference': home_conference,
    }


def extract_date_from_url(url: str) -> str:
    """
    Extracts the date from the given URL and returns it as a human-readable string.

    :param url: The target URL
    :return: Human-readable date string
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')

    # Extract the year, month, and day from the URL path
    year = int(path_parts[-4])
    month = int(path_parts[-3])
    day = int(path_parts[-2])

    # Create a date object
    date_obj = datetime.date(year, month, day)

    # Return the date as a human-readable string
    return date_obj.strftime("%B %d, %Y")

def fetch_matches(target_url: str, target_gender: str, target_division: str):
    """
    Fetch the matches from the specified URL

    :param target_url: URL to fetch the matches
    :param target_gender: Gender
    :param target_division: Division
    :return: List of matches
    """
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(['HEAD', 'GET', 'OPTIONS'])
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = None
    for attempt in range(retry.total):
        response = None
        try:
            response = session.get(target_url, timeout=10)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            error_type = type(e).__name__
            if response is not None and response.status_code == 429:
                print(f"Throttling detected. Retrying after delay...")
                time.sleep(2 ** retry.total)
            elif response is not None and response.status_code == 404:
                print(f"No data found for {extract_date_from_url(target_url)}")
                return []
            elif response is not None:
                print(f"Failed to fetch data from {target_url}: {e} (Error: {error_type})")
                print(f"\tThe status code is {response.status_code}")
                return []
            else:
                print(f"Failed to fetch data from {target_url}: {e} (Error: {error_type})")
                return []

    if response is None:
        print(f"Failed to fetch data from {target_url}")
        return []

    data = response.json()
    games = data.get('games', [])
    if len(games) == 0:
        return []

    updated_at = data.get('updated_at')

    # Here updated_at is a string in the format of "09-28-2024 02:24:34"
    # We need to convert it to a Unix timestamp
    updated_at = int(time.mktime(time.strptime(updated_at, "%m-%d-%Y %H:%M:%S")))

    fetched_matches = []
    for item in games:
        game = item.get('game')
        if game is None:
            continue

        match_data = extract_match_data(game, target_gender, target_division, updated_at)
        if match_data:
            fetched_matches.append(match_data)

    return fetched_matches


def send_match_to_sqs(queue_url: str, match: dict):
    """
    Send a match to the SQS queue

    :param match: Match dictionary
    """
    # print(f"Todo: Send match to SQS {match}")
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(match)
    )

def send_matches_to_sqs(queue_url: str, matches: list[dict]):
    """
    Send the matches to the SQS queue

    :param matches: List of matches
    """
    for current_match in matches:
        send_match_to_sqs(queue_url, current_match)


if __name__ == "__main__":
    genders = ['male', 'female']
    divisions = ['d1', 'd2']
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=4) # 3 Days before the end date

    url_iterator = URLIterator(genders, divisions, start_date, end_date)

    all_matches = []
    for url in url_iterator:
        current_gender = url_iterator.get_current_gender()
        current_division = url_iterator.get_current_division()
        all_matches.extend(fetch_matches(url, current_gender, current_division))

    # Sort the matches first by gender, then by state putting final matches first, then by startTimeEpoch
    all_matches.sort(key=lambda x: (x['gender'], x['matchState'] != 'final', x['startTimeEpoch']))

    send_matches_to_sqs(QUEUE_URL, all_matches)

    print(f"Total Matches: {len(all_matches)}")
    print(f"Total URLs Processed: {url_iterator.get_counter()}")
    print("Done!")

