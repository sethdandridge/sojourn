#!/bin/bash
gunicorn -w 5 -b 0.0.0.0:80 --preload "app:create_app()"
