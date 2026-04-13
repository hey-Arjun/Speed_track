import requests

API_URL = "http://127.0.0.1:8000/alert"

def send_event(event):
    try:
        response = requests.post(API_URL, json=event)
        print("Sent:", event, "Status:", response.status_code)
    except Exception as e:
        print("API Error:",  e)
