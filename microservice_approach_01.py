from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from celery import Celery
import requests
import xmltodict
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
CORS(app)
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)
    sell_mode = db.Column(db.String, nullable=False)

db.create_all()

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

@celery.task
def fetch_events():
    response = requests.get('https://provider.code-challenge.feverup.com/api/events')
    if response.status_code == 200:
        events_data = xmltodict.parse(response.content)
        for event in events_data['events']['event']:
            event_id = event['id']
            sell_mode = event['sell_mode']
            if sell_mode == 'online':
                existing_event = Event.query.get(event_id)
                if existing_event:
                    existing_event.name = event['name']
                    existing_event.start_date = event['start_date']
                    existing_event.end_date = event['end_date']
                    existing_event.sell_mode = sell_mode
                else:
                    new_event = Event(
                        id=event_id,
                        name=event['name'],
                        start_date=event['start_date'],
                        end_date=event['end_date'],
                        sell_mode=sell_mode
                    )
                    db.session.add(new_event)
        db.session.commit()

@app.route('/events', methods=['GET'])
def get_events():
    starts_at = request.args.get('starts_at')
    ends_at = request.args.get('ends_at')
    if not starts_at or not ends_at:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    filtered_events = Event.query.filter(
        Event.start_date >= starts_at,
        Event.end_date <= ends_at
    ).all()
    
    return jsonify([{
        'id': event.id,
        'name': event.name,
        'start_date': event.start_date,
        'end_date': event.end_date,
        'sell_mode': event.sell_mode
    } for event in filtered_events])

if __name__ == '__main__':
    app.run(debug=True)
