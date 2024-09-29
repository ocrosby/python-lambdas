import json
import pytest

from lambdas.fetch_ncaa_matches.handler import lambda_handler

# Define test cases
test_cases = [
    {
        "name": "Female DI 09/01/2024",
        "event": {
            "gender": "female",
            "division": "d1",
            "target_date": "2024-09-01"
        },
        "context": {},
        "expected": {
            "statusCode": 200,
            "count": 132,
            "matches": [
                {
                    "id": 5398675,
                    "processTimeEpoch": 1727622904,
                    "startTimeEpoch": 1725206400,
                    "matchState": "final",
                    "updatedAt": 1727558443,
                    "awayTeam": "Eastern Illinois University",
                    "awayScore": 2,
                    "awayConference": "OVC",
                    "homeTeam": "Eastern Kentucky University",
                    "homeScore": 2,
                    "homeConference": "ASUN"
                }
            ]
        }
    },
    # Add more test cases here if needed
]


@pytest.mark.parametrize("test_case", test_cases, ids=[tc["name"] for tc in test_cases])
def test_lambda_handler(test_case):
    # Arrange
    event = test_case.get("event")
    context = test_case.get("context")
    expected = test_case.get("expected")

    # Act
    response = lambda_handler(event, context)

    # Assert
    body = response.get("body")
    data = json.loads(body)

    actual_status = response.get("statusCode")
    expected_status = expected.get("statusCode")

    actual_count = len(data)
    expected_count = expected.get("count")

    expected_matches = expected.get("matches")

    assert actual_status == expected_status, f"Expected status {expected_status} got {actual_status}"
    assert actual_count == expected_count, f"Expected count {expected_count} got {actual_count}"

    for i, match in enumerate(expected_matches):
        expected_match = expected_matches[i]
        assert match.get("id") == expected_match.get("id"), f"Expected id {expected_match.get('id')} got {match.get('id')}"
        assert match.get("processTimeEpoch") == expected_match.get("processTimeEpoch"), f"Expected processTimeEpoch {expected_match.get('processTimeEpoch')} got {match.get('processTimeEpoch')}"
        assert match.get("startTimeEpoch") == expected_match.get("startTimeEpoch"), f"Expected startTimeEpoch {expected_match.get('startTimeEpoch')} got {match.get('startTimeEpoch')}"
        assert match.get("matchState") == expected_match.get("matchState"), f"Expected matchState {expected_match.get('matchState')} got {match.get('matchState')}"
        assert match.get("updatedAt") == expected_match.get("updatedAt"), f"Expected updatedAt {expected_match.get('updatedAt')} got {match.get('updatedAt')}"
        assert match.get("awayTeam") == expected_match.get("awayTeam"), f"Expected awayTeam {expected_match.get('awayTeam')} got {match.get('awayTeam')}"
        assert match.get("awayScore") == expected_match.get("awayScore"), f"Expected awayScore {expected_match.get('awayScore')} got {match.get('awayScore')}"
        assert match.get("awayConference") == expected_match.get("awayConference"), f"Expected awayConference {expected_match.get('awayConference')} got {match.get('awayConference')}"
        assert match.get("homeTeam") == expected_match.get("homeTeam"), f"Expected homeTeam {expected_match.get('homeTeam')} got {match.get('homeTeam')}"
        assert match.get("homeScore") == expected_match.get("homeScore"), f"Expected homeScore {expected_match.get('homeScore')} got {match.get('homeScore')}"
        assert match.get("homeConference") == expected_match.get("homeConference"), f"Expected homeConference {expected_match.get('homeConference')} got {match.get('homeConference')}"
