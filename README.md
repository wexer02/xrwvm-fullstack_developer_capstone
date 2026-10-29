# fullstack_developer_capstone

Cars Dealership - Full Stack Development Capstone

Deployed application: https://cars-dealership.2gigbvkbdmwi.us-south.codeengine.appdomain.cloud/

A car dealership review application built from IBM Skills Network's
[course starter](https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone).

Visitors can browse 50 dealerships, filter by state, and read reviews with
sentiment analysis. Registered users can sign in and post vehicle purchase
reviews. Django admin manages users, car makes, and car models.

## Components

- React frontend in `server/frontend`, built with Vite.
- Django authentication, admin, car catalog and API gateway in `server/djangoapp`.
- Node.js/Express and MongoDB dealer/review service in `server/database`.
- Flask/NLTK VADER sentiment service using the bundled course lexicon.
- Docker image and Kubernetes deployment manifest; IBM Code Engine hosting.
- GitHub Actions builds the frontend, runs Django tests, builds the Docker
  image, and tests the real microservices and review round-trip.

## Run locally

```sh
docker compose up --build
```

Open http://127.0.0.1:8000, then use Sign Up to create a demonstration account.
All public access uses Django on port 8000. MongoDB and the private microservices
are bound to loopback inside the container. CSRF protection and authenticated
review submission are enforced by the server.

## Tests

```sh
python -m pip install -r server/requirements.txt
npm ci --prefix server/frontend
npm run build --prefix server/frontend
cd server
python manage.py test djangoapp
```

With the complete application running, execute `python server/integration_check.py`
from the repository root. Set `APP_URL` to test a deployed instance.

## Course deployment scope

The course deployment runs the components together in one container, with
minimum and maximum scale set to one. Its databases are demonstration data;
the course cloud filesystem and lab can be reset. Local Docker Compose mounts
a named volume to preserve data. A production deployment should use persistent
managed databases, separate service deployments, and a stable externally
provided `DJANGO_SECRET_KEY`.

Team profiles and contact details on the static pages are demonstration content.
Portrait photographs come from Random User's public example portrait collection.
The course starter's license is retained in LICENSE.
