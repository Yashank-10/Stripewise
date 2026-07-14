# this provide template for email which is sent by providers
def purchase_confirmation_email(
    customer_name,
    tier,
):
    subject = f"Welcome to {tier.title()}!"

    html = f"""
    <h1>Payment Successful!! 🎉</h1>

    <p>Hi {customer_name},</p>

    <p>
        Thank you for purchasing the
        <strong>{tier.title()}</strong>
        plan.
    </p>

    <p>
        Your account has been activated.
    </p>

    <p>
        Enjoy building with our platform!
    </p>
    """

    return subject, html