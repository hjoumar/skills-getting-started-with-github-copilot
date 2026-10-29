# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- See signed-up participants in each activity card, updated after signing up
- Activity refreshes keep the latest results even when requests finish out of order
- Sign up for activities
- Unregister a participant using the trash icon beside their email; cards refresh automatically

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## Backend Tests

From the repository root, install the dependencies and run the backend tests:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -v
```

The pytest tests in `tests/test_activities.py` cover signup and unregister behavior
using FastAPI TestClient and the Arrange-Act-Assert (AAA) pattern. Fixtures in
`tests/conftest.py` provide isolated activity data for each test and restore the
original data afterward. No running server or database is required.

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/signup?email=student@mergington.edu` | Unregister a participant; returns 404 if the activity or registration does not exist |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
