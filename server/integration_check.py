"""Exercise real Django, Node/MongoDB and Flask services."""
import os
import time
import uuid
import requests

base = os.getenv('APP_URL', 'http://127.0.0.1:8000').rstrip('/')
session = requests.Session()


def post(path, data):
    token = session.get(base + '/djangoapp/csrf', timeout=20).json()['csrfToken']
    return session.post(base + '/djangoapp/' + path, json=data, headers={'X-CSRFToken': token}, timeout=20)


for attempt in range(60):
    try:
        response = session.get(base + '/djangoapp/get_dealers', timeout=3)
        if response.ok and len(response.json()['dealers']) == 50:
            break
    except requests.RequestException:
        pass
    time.sleep(1)
else:
    raise RuntimeError('Services did not become ready.')

dealers = response.json()['dealers']
assert session.get(base + '/').status_code == 200
for page in ['/about', '/contact']:
    assert session.get(base + page).status_code == 200
kansas = session.get(base + '/djangoapp/get_dealers/Kansas').json()['dealers']
assert kansas and all(dealer['state'] == 'Kansas' for dealer in kansas)
dealer_id = dealers[0]['id']
assert session.get(base + f'/djangoapp/dealer/{dealer_id}').json()['dealer'][0]['id'] == dealer_id
catalog = session.get(base + '/djangoapp/get_cars').json()
assert len(catalog['CarMakes']) == 5 and len(catalog['CarModels']) > 50
for text, sentiment in [('Fantastic services', 'positive'), ('Terrible service, I hate it', 'negative'), ('The car is parked', 'neutral')]:
    assert session.get(base + '/djangoapp/analyze/' + requests.utils.quote(text)).json()['sentiment'] == sentiment
assert post('add_review', {}).status_code == 401
username = 'check_' + uuid.uuid4().hex[:10]
password = 'Capstone-Integration-2026!'
assert post('register', {'username': username, 'first_name': 'Integration', 'last_name': 'Driver',
                         'email': username + '@example.com', 'password': password}).status_code == 200
car = catalog['CarModels'][0]
text = 'Fantastic services. Integration check ' + username
assert post('add_review', {'dealership': dealer_id, 'review': text, 'car_make': car['CarMake'],
                           'car_model': car['CarModel'], 'car_year': 2023, 'purchase_date': '2026-01-01'}).status_code == 200
reviews = session.get(base + f'/djangoapp/reviews/dealer/{dealer_id}').json()['reviews']
assert any(review['review'] == text and review['sentiment'] == 'positive' for review in reviews)
assert post('logout', {}).status_code == 200
assert not session.get(base + '/djangoapp/session').json()['authenticated']
assert post('login', {'userName': username, 'password': password}).json()['status'] == 'Authenticated'
assert post('logout', {}).status_code == 200
print('PASS: 50 dealers; Kansas filter; dealer details; 5 makes and all models; three sentiments; CSRF-protected registration/login/logout; authenticated MongoDB review round-trip.')
