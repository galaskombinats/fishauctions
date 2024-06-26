from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fishauction.settings')

app = Celery('fishauction')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'check-and-end-auctions-every-minute': {
        'task': 'auction.tasks.end_auction_task',
        'schedule': crontab(minute='*/1'),  # Adjust the schedule as needed
    },
}
