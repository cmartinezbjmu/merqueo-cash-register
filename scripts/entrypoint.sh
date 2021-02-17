#!/bin/sh

set -e

# Migrate database
python manage.py migrate

# Load default denomination currencies
python manage.py loaddata currency_denomination_fixtures
python manage.py loaddata available_cash_fixtures

# Start Django app
python manage.py runserver 127.0.0.1:8000
