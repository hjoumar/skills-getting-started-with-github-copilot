from copy import deepcopy

import pytest


ENDPOINT = "/activities/Test%20Activity/signup"
EMAIL = "student+test@example.com"


def test_signup_adds_participant(client, activity_data):
    # Arrange
    expected = deepcopy(activity_data)
    expected["Test Activity"]["participants"].append(EMAIL)

    # Act
    response = client.post(ENDPOINT, params={"email": EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {EMAIL} for Test Activity"}
    assert activity_data == expected


def test_duplicate_signup_is_rejected(client, activity_data):
    # Arrange
    activity_data["Test Activity"]["participants"].append(EMAIL)
    expected = deepcopy(activity_data)

    # Act
    response = client.post(ENDPOINT, params={"email": EMAIL})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activity_data == expected


@pytest.mark.parametrize("method", ["post", "delete"])
def test_unknown_activity_is_rejected(client, activity_data, method):
    # Arrange
    expected = deepcopy(activity_data)

    # Act
    response = client.request(
        method, "/activities/Missing/signup", params={"email": EMAIL}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_data == expected


@pytest.mark.parametrize("method", ["post", "delete"])
def test_missing_email_is_rejected(client, activity_data, method):
    # Arrange
    expected = deepcopy(activity_data)

    # Act
    response = client.request(method, ENDPOINT)

    # Assert
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        error["loc"] == ["query", "email"] and error["type"] == "missing"
        for error in errors
    )
    assert activity_data == expected


def test_unregister_removes_only_selected_participant(client, activity_data):
    # Arrange
    activity_data["Test Activity"]["participants"] = [EMAIL, "remaining@example.com"]
    expected = deepcopy(activity_data)
    expected["Test Activity"]["participants"].remove(EMAIL)

    # Act
    response = client.delete(ENDPOINT, params={"email": EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {EMAIL} from Test Activity"}
    assert activity_data == expected


def test_unregister_last_participant_leaves_empty_list(client, activity_data):
    # Arrange
    activity_data["Test Activity"]["participants"].append(EMAIL)
    expected = deepcopy(activity_data)
    expected["Test Activity"]["participants"] = []

    # Act
    response = client.delete(ENDPOINT, params={"email": EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {EMAIL} from Test Activity"}
    assert activity_data == expected


def test_missing_registration_is_rejected(client, activity_data):
    # Arrange
    expected = deepcopy(activity_data)

    # Act
    response = client.delete(ENDPOINT, params={"email": EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert activity_data == expected


def test_participant_can_sign_up_again_after_unregistering(client, activity_data):
    # Arrange
    activity_data["Test Activity"]["participants"].append(EMAIL)
    removed = client.delete(ENDPOINT, params={"email": EMAIL})
    assert removed.status_code == 200
    assert activity_data["Test Activity"]["participants"] == []
    expected = deepcopy(activity_data)
    expected["Test Activity"]["participants"].append(EMAIL)

    # Act
    response = client.post(ENDPOINT, params={"email": EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {EMAIL} for Test Activity"}
    assert activity_data == expected
