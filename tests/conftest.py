from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def activity_data():
    original_activities = deepcopy(activities)
    activities.clear()
    activities.update({
        "Test Activity": {
            "description": "Test activity",
            "schedule": "Mondays",
            "max_participants": 10,
            "participants": [],
        },
        "Other Activity": {
            "description": "Unrelated activity",
            "schedule": "Fridays",
            "max_participants": 5,
            "participants": ["other@example.com"],
        },
    })
    try:
        yield activities
    finally:
        activities.clear()
        activities.update(original_activities)


@pytest.fixture
def client(activity_data):
    with TestClient(app) as test_client:
        yield test_client
