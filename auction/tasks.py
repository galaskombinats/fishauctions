from celery import shared_task
from .models import Auction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def end_auction_task():
    current_time = timezone.now()
    print(f"[DEBUG] Running end_auction_task at {current_time}")
    logger.info(f"Running end_auction_task at {current_time}")

    auctions_to_end = Auction.objects.filter(is_ended=False, end_time__lte=current_time)
    print(f"[DEBUG] Found {auctions_to_end.count()} auctions to end.")

    for auction in auctions_to_end:
        auction.is_ended = True
        auction.save()
        print(f"[DEBUG] Auction {auction.id} ({auction.title}) ended successfully at {current_time}")
        logger.info(f"Auction {auction.id} ({auction.title}) ended successfully at {current_time}")

    if not auctions_to_end:
        print("[DEBUG] No auctions to end at this time.")
        logger.info("No auctions to end at this time.")
