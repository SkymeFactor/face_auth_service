#!/bin/bash
celery -A utils.celery_tasks --workdir=./app worker -l INFO --logfile=../.logs/celery.log
