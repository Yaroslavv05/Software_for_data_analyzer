import logging

from django.dispatch import receiver
from django.db.models.signals import post_save

from main.models import Template
from main.tasks import get_settings_from_model

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Template)
def get_settings_from_model(sender, instance, **kwargs):
    """
    When object is created in database, its started celery task.
    Its shold provide data to celery task
    """
    try:
        get_settings_from_model.delay(instance)
        logging.info(f"Send to celery task with settings: {instance}")
    except Exception as e:
        logger.info(f"An error occurred while getting settings from model: {e}")
