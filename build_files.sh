#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput 2>/dev/null || true
