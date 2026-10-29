import json
from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import Client, TestCase
from .models import CarMake, CarModel


class DealershipTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='Testing-Reviews-2026!')

    def post(self, endpoint, payload):
        return self.client.post('/djangoapp/' + endpoint, json.dumps(payload), content_type='application/json')

    def test_login_and_logout_session(self):
        self.assertEqual(self.post('login', {'userName': 'tester', 'password': 'wrong'}).status_code, 401)
        self.assertEqual(self.post('login', {'userName': 'tester', 'password': 'Testing-Reviews-2026!'}).json()['status'], 'Authenticated')
        self.assertTrue(self.client.get('/djangoapp/session').json()['authenticated'])
        self.assertEqual(self.post('logout', {}).status_code, 200)
        self.assertFalse(self.client.get('/djangoapp/session').json()['authenticated'])

    def test_course_get_logout_clears_session(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/djangoapp/logout').json(), {'userName': ''})
        self.assertFalse(self.client.get('/djangoapp/session').json()['authenticated'])

    def test_post_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post('/djangoapp/login', '{}', content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_registration_validation_and_password_hash(self):
        self.assertEqual(self.post('register', {}).status_code, 400)
        payload = {'username': 'newdriver', 'first_name': 'Sam', 'last_name': 'Driver',
                   'email': 'sam@example.com', 'password': 'Driver-Review-2026!'}
        self.assertEqual(self.post('register', payload).status_code, 200)
        self.assertTrue(User.objects.get(username='newdriver').check_password(payload['password']))
        self.assertEqual(self.post('register', payload).status_code, 400)

    @patch('djangoapp.views.get_request')
    def test_filter_and_missing_dealer(self, get):
        get.return_value = [{'id': 1, 'state': 'Kansas'}]
        self.assertEqual(self.client.get('/djangoapp/get_dealers/Kansas').json()['dealers'][0]['state'], 'Kansas')
        get.assert_called_with('fetchDealers/Kansas')
        get.return_value = []
        self.assertEqual(self.client.get('/djangoapp/dealer/99999').status_code, 404)

    @patch('djangoapp.views.post_review')
    def test_review_requires_login_and_uses_authenticated_author(self, post):
        make = CarMake.objects.create(name='Toyota')
        CarModel.objects.create(car_make=make, name='Camry', type='Sedan', year=2023)
        payload = {'name': 'Forged identity', 'dealership': 1, 'review': 'Fantastic services',
                   'car_make': 'Toyota', 'car_model': 'Camry', 'car_year': 2023, 'purchase_date': '2026-01-01'}
        self.assertEqual(self.post('add_review', payload).status_code, 401)
        self.client.force_login(self.user)
        post.return_value = {'id': 51}
        self.assertEqual(self.post('add_review', payload).status_code, 200)
        self.assertEqual(post.call_args.args[0]['name'], 'tester')
        payload['review'] = '  '
        self.assertEqual(self.post('add_review', payload).status_code, 400)

    def test_car_catalog_contains_make_and_model(self):
        make = CarMake.objects.create(name='Toyota', description='Toyota vehicles')
        CarModel.objects.create(car_make=make, name='Camry', type='Sedan', year=2023)
        result = self.client.get('/djangoapp/get_cars').json()
        self.assertEqual(result['CarMakes'][0]['name'], 'Toyota')
        self.assertEqual(result['CarModels'][0]['CarModel'], 'Camry')
