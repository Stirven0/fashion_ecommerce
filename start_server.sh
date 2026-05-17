#!/bin/bash
cd /home/fashion_store
DATABASE_URL=sqlite:///db.sqlite3 uv run python manage.py runserver 0.0.0.0:8000 --noreload
