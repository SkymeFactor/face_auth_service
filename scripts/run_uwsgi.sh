#!/bin/bash
uwsgi --vacuum --lazy-apps --workers 4 --threads 2 --https 0.0.0.0:5000,ssl/security.crt,ssl/security.key --chdir app -w wsgi:app