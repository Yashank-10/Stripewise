from app.emails.providers import initialize_resend
from app.emails.templates import purchase_confirmation_email

import resend
import logging

logger = logging.getLogger(__name__)

# Sends purchase confirmation mail to customer after successful payment
def send_purchase_confirmation(
    customer_name,
    customer_email,
    tier,
):
    initialize_resend()

    subject, html = purchase_confirmation_email(
        customer_name,
        tier,
    )
    logger.info(
        "Preparing purchase confirmation email for %s",
        customer_email,
    )
    
    try:
        response = resend.Emails.send(
            {
                "from": "Acme <onboarding@resend.dev>",
                "to": customer_email,
                "subject": subject,
                "html": html,
            }
        )

        logger.info(
            "Purchase confirmation email sent to %s",
            customer_email,
        )

        return response

    except Exception:
        logger.exception(
            "Failed to send purchase confirmation email to %s",
            customer_email,
        )
        raise