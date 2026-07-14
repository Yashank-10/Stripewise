import resend
from flask import current_app

# communicate with the resend API to send emails
# this sends mail created by template 

def initialize_resend():
    
    resend.api_key = current_app.config["RESEND_API_KEY"]