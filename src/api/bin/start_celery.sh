#!/bin/bash
celery -A bkuser_core worker -l info --concurrency=8 --max-tasks-per-child=1
