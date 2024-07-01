from flask import Flask, request, jsonify
import requests
import threading
import time
import xml.etree.ElementTree as ET

app = Flask(__name__)

# In-memory storage for events
events = {}
last_fetch_time = None

# Periodically fetch events
def fetch_events():
    global last_fetch_time
    while True:
        response = requests.get('https://provider.code-challenge.feverup.com/api/events')
        if response.status_code == 200:
            xml_root = ET.fromstring(response.content)
            for event in xml_root.findall('event'):
                event_id = event.find('id').text
                sell_mode = event.find('sell_mode').text
                if sell_mode == 'online':
                    events[event_id] = {
                        'id': event_id,
                        'name': event.find('name').text,
                        'start_date': event.find('start_date').text,
                        'end_date': event.find('end_date').text,
                        'sell_mode': sell_mode
                    }
            last_fetch_time = time.time()
        time.sleep(60)  # Fetch every 60 seconds

# Start the background thread for fetching events
threading.Thread(target=fetch_events, daemon=True).start()

@app.route('/events', methods=['GET'])
def get_events():
    starts_at = request.args.get('starts_at')
    ends_at = request.args.get('ends_at')
    if not starts_at or not ends_at:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    filtered_events = [
        event for event in events.values()
        if event['start_date'] >= starts_at and event['end_date'] <= ends_at
    ]
    return jsonify(filtered_events)

if __name__ == '__main__':
    app.run()
