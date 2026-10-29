"""Session authentication and the course dealership API."""
import json
from datetime import date
from urllib.parse import quote
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_POST
from .models import CarMake, CarModel
from .restapis import analyze_review_sentiments, get_request, post_review


def error(message, status=400):
    return JsonResponse({'status': status, 'message': message}, status=status)


def body(request):
    value = json.loads(request.body)
    if not isinstance(value, dict):
        raise ValueError('A JSON object is required.')
    return value


@require_GET
def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})


@require_GET
def session_user(request):
    user = request.user
    return JsonResponse({'authenticated': user.is_authenticated,
                         'userName': user.username if user.is_authenticated else ''})


@require_POST
def login_user(request):
    try:
        data = body(request)
        user = authenticate(request, username=data.get('userName', ''), password=data.get('password', ''))
    except (ValueError, TypeError):
        return error('Invalid login data.')
    if user is None:
        return error('Invalid username or password.', 401)
    login(request, user)
    return JsonResponse({'userName': user.username, 'status': 'Authenticated'})


@require_POST
def logout_request(request):
    logout(request)
    return JsonResponse({'status': 200, 'message': 'Logged out successfully'})


@require_POST
def registration(request):
    try:
        data = body(request)
        values = {key: str(data.get(key, '')).strip() for key in ('username', 'first_name', 'last_name', 'email')}
        if not all(values.values()) or not data.get('password'):
            return error('All five fields are required.')
        if len(values['username']) > 150 or any(len(values[key]) > 150 for key in ('first_name', 'last_name')):
            return error('Name fields are too long.')
        validate_email(values['email'])
        candidate = User(**values)
        candidate.full_clean(exclude=['password'])
        validate_password(data['password'], candidate)
        user = User.objects.create_user(password=data['password'], **values)
    except (ValueError, TypeError, ValidationError, IntegrityError):
        return error('Use a unique username, valid email, and a strong password.')
    login(request, user)
    return JsonResponse({'status': 200, 'userName': user.username})


@require_GET
def get_dealerships(request, state='All'):
    try:
        endpoint = 'fetchDealers' if state == 'All' else 'fetchDealers/' + quote(state, safe='')
        return JsonResponse({'status': 200, 'dealers': get_request(endpoint)})
    except requests.RequestException:
        return error('Dealer service is temporarily unavailable.', 503)


@require_GET
def get_dealer_details(request, dealer_id):
    try:
        dealers = get_request(f'fetchDealer/{dealer_id}')
        if not dealers:
            return error('Dealer not found.', 404)
        return JsonResponse({'status': 200, 'dealer': dealers})
    except requests.RequestException:
        return error('Dealer service is temporarily unavailable.', 503)


@require_GET
def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request(f'fetchReviews/dealer/{dealer_id}')
        for review in reviews:
            review['sentiment'] = analyze_review_sentiments(review['review'])
        return JsonResponse({'status': 200, 'reviews': reviews})
    except requests.RequestException:
        return error('Review service is temporarily unavailable.', 503)


@require_GET
def get_cars(request):
    models = [{'CarMake': car.car_make.name, 'CarModel': car.name, 'year': car.year, 'type': car.type}
              for car in CarModel.objects.select_related('car_make').order_by('car_make__name', 'name', 'year')]
    return JsonResponse({'status': 200, 'CarMakes': list(CarMake.objects.values('id', 'name', 'description')),
                         'CarModels': models})


@require_GET
def analyze_review(request, text):
    try:
        return JsonResponse({'text': text, 'sentiment': analyze_review_sentiments(text)})
    except requests.RequestException:
        return error('Sentiment service is temporarily unavailable.', 503)


@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return error('Sign in before posting a review.', 401)
    try:
        data = body(request)
        text = str(data.get('review', '')).strip()
        year = int(data.get('car_year', 0))
        dealer_id = int(data.get('dealership', 0))
        purchased = date.fromisoformat(data.get('purchase_date', ''))
        if not 1 <= len(text) <= 5000 or not 2015 <= year <= date.today().year or purchased > date.today() or dealer_id < 1:
            return error('Enter a review, valid vehicle year and purchase date.')
        make, model = data.get('car_make'), data.get('car_model')
        if not CarModel.objects.filter(car_make__name=make, name=model).exists():
            return error('Select a vehicle from the catalog.')
        review = {'name': request.user.get_full_name() or request.user.username,
                  'dealership': dealer_id, 'review': text, 'purchase': True,
                  'purchase_date': purchased.isoformat(), 'car_make': make,
                  'car_model': model, 'car_year': year}
        return JsonResponse({'status': 200, 'review': post_review(review)})
    except (ValueError, TypeError):
        return error('Invalid review data.')
    except requests.RequestException:
        return error('Unable to save the review. Please try again.', 503)
