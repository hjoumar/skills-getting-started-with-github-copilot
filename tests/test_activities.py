import unittest
from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = deepcopy(activities)
        activities["Test Activity"] = {
            "description": "Test activity",
            "schedule": "Mondays",
            "max_participants": 10,
            "participants": [],
        }
        self.client = TestClient(app)
        self.endpoint = "/activities/Test%20Activity/signup"
        self.params = {"email": "student+test@example.com"}

    def tearDown(self):
        self.client.close()
        activities.clear()
        activities.update(self.original_activities)

    def test_signup_unregister_and_signup_again(self):
        self.assertEqual(self.client.post(self.endpoint, params=self.params).status_code, 200)
        response = self.client.delete(self.endpoint, params=self.params)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unregistered student+test@example.com", response.json()["message"])
        self.assertEqual(self.client.get("/activities").json()["Test Activity"]["participants"], [])
        self.assertEqual(self.client.post(self.endpoint, params=self.params).status_code, 200)

    def test_unregister_only_removes_selected_participant(self):
        activities["Test Activity"]["participants"] = [self.params["email"], "other@example.com"]
        response = self.client.delete(self.endpoint, params=self.params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.get("/activities").json()["Test Activity"]["participants"],
            ["other@example.com"],
        )

    def test_unknown_activity_returns_not_found(self):
        response = self.client.delete("/activities/Missing/signup", params=self.params)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Activity not found")

    def test_missing_registration_returns_not_found(self):
        response = self.client.delete(self.endpoint, params=self.params)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Student is not signed up for this activity")
        self.assertEqual(activities["Test Activity"]["participants"], [])

    def test_duplicate_signup_still_rejected(self):
        self.assertEqual(self.client.post(self.endpoint, params=self.params).status_code, 200)
        self.assertEqual(self.client.post(self.endpoint, params=self.params).status_code, 400)
        self.assertEqual(activities["Test Activity"]["participants"], [self.params["email"]])


if __name__ == "__main__":
    unittest.main()
