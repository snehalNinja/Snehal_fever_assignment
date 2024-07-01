### README.md

# Event Finder with Flask, Celery, and Redis : Approach 1

This project is a robust and scalable solution for fetching and querying event data from an external provider using Flask, Celery, and Redis. The application is designed to handle periodic tasks asynchronously and efficiently manage event data using a SQLite database.

## Overview

- **Flask Application**: Handles HTTP requests and provides an API endpoint for querying events.
- **SQLAlchemy**: Used for database interactions, storing events in a SQLite database.
- **Celery**: Manages the periodic task of fetching events from an external API.
- **Redis**: Serves as the message broker for Celery tasks.
- **Front-End**: A simple HTML, CSS, and JavaScript interface that allows users to input date ranges and view events.

## Detailed Steps

### 1. Flask Application

- **Flask Configuration**: The Flask application is configured to use SQLAlchemy for the database and Celery for asynchronous tasks. CORS is enabled to allow cross-origin requests from the frontend.
- **Event Model**: A SQLAlchemy model `Event` is defined to represent event data in the database. The model includes fields for `id`, `name`, `start_date`, `end_date`, and `sell_mode`.
- **API Endpoint**: The `/events` endpoint accepts `starts_at` and `ends_at` parameters, queries the database for events within this date range, and returns the results in JSON format.

### 2. Celery Configuration

- **Celery Setup**: The `make_celery` function initializes Celery with the Flask application context, allowing tasks to interact with Flask's application context.
- **Periodic Task**: The `fetch_events` task is defined to periodically fetch events from the external API, process the data, and update the database. This task runs every 60 seconds as configured in the Celery beat schedule in `worker.py`.

### 3. Periodic Fetching with Celery

- **Fetching Events**: The `fetch_events` task sends a GET request to the external API to retrieve event data. The response is parsed using `xmltodict`.
- **Database Update**: For each event with a sell mode of "online", the task checks if the event already exists in the database:
  - If the event exists, it updates the event details.
  - If the event does not exist, it adds a new event to the database.
- **Commit Changes**: Changes are committed to the database after processing all events.


## Running the Application

### Start the Flask Application

Run the Flask application to start the server that handles API requests.

```sh
python app.py
```

### Start the Celery Worker

Run the Celery worker with beat to handle periodic tasks. Ensure Redis is running as the message broker.

```sh
docker run -d -p 6379:6379 redis
celery -A worker worker --beat
```



## Key Points

- **Separation of Concerns**: The approach separates the concerns of fetching and storing event data (handled by Celery) from serving and querying event data (handled by Flask).
- **Asynchronous Processing**: By using Celery, the time-consuming task of fetching data from an external API does not block the main application, keeping the API responsive.
- **Scalability**: The use of a database ensures persistence and efficient querying of event data, even if the external API is temporarily unavailable.
- **Periodic Updates**: The Celery beat scheduler ensures that the event data is periodically updated, providing up-to-date information to users.

This approach provides a robust and scalable solution for integrating with an external event provider, leveraging the power of asynchronous processing with Celery and efficient data management with Flask and SQLAlchemy.


## Approach 2: In-Memory Storage with Periodic Fetching

### Steps:

1. **Fetch Events Periodically**: 
   - Set up a background task to periodically fetch events from the external provider's API and store them in an in-memory data structure (like a dictionary).

2. **Filter and Store Relevant Events**: 
   - Filter out events with a sell mode other than "online" and store the relevant events in the in-memory data structure with their timestamps.

3. **Expose the API Endpoint**: 
   - Implement the API endpoint that accepts `starts_at` and `ends_at` parameters and returns events within the specified time range.

4. **In-Memory Data Structure**: 
   - Use a dictionary with event IDs as keys and event details as values. Also, store timestamps to track the availability of events.

5. **Handle External API Downtime**: 
   - Since the data is stored in memory, the endpoint can still return results even if the external API is down.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/event-finder.git
cd event-finder
```

2. Install the required packages:

```sh
pip install Flask requests
```

## Usage

1. Start the Flask application:

```sh
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`.

3. Use the `/events` endpoint to query events:

```sh
GET /events?starts_at=YYYY-MM-DD&ends_at=YYYY-MM-DD
```

## Example

To get events between `2024-06-01` and `2024-06-30`, you can send a GET request to:

```
http://localhost:5000/events?starts_at=2024-06-01&ends_at=2024-06-30
```

## Notes

- Events are fetched every 60 seconds in the background.
- Only events with a sell mode of "online" are stored and returned by the API.
# Snehal_fever_assignment
