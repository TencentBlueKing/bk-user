#!/bin/bash
celery -A bkuser_core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
