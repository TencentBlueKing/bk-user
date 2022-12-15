# -*- coding: utf-8 -*-
import logging

from bkuser_core.celery import app
from bkuser_core.common.notifier import send_sms

logger = logging.getLogger(__name__)


@app.task
def send_reset_password_verification_code_sms(profile_id: str, send_config: dict):
    try:
        logger.info(
            "going to send verification_code of Profile(%s) via telephone(%s)",
            profile_id,
            send_config["receivers"],
        )
        send_sms(**send_config)
    except Exception as e:
        logger.info(
            "Failed to send verification_code of Profile(%s) via telephone(%s): %s",
            profile_id,
            send_config["receivers"],
            e,
        )
