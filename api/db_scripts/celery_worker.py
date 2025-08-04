from celery import Celery
from celery.schedules import crontab

app = Celery(
    'swish_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

app.conf.beat_schedule = {
    'load-current-player-rankings-every-2-days': {
        'task': 'insert_current_rankings_table.load_current_player_rankings',
        # run every 2 days at midnight
        'schedule': crontab(hour=0, minute=0, day_of_month='*/2'),
    },
}

app.conf.timezone = 'UTC'  # or your timezone

import insert_current_rankings_table
