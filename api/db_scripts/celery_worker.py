from celery import Celery

app = Celery(
    'swish_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

import insert_current_rankings_table