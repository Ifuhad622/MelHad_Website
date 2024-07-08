from flask import Flask, Blueprint, render_template, request, jsonify
import stripe
import sendgrid
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import yaml

app = Flask(__name__)

# Load configuration from config.yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Configure Stripe
stripe.api_key = config['stripe']['secret_key']

# Configure SendGrid
sg = sendgrid.SendGridAPIClient(config['sendgrid']['api_key'])

# Configure Twilio
twilio_client = Client(config['twilio']['account_sid'], config['twilio']['auth_token'])

# Blueprint for main routes
main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def home():
    return render_template('index.html')

@main_blueprint.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    data = request.json
    amount = data['amount']
    currency = data.get('currency', 'usd')
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        payment_method_types=["card"],
    )
    return jsonify(client_secret=intent['client_secret'])

@main_blueprint.route('/send-invoice', methods=['POST'])
def send_invoice():
    data = request.json
    recipient_email = data['email']
    recipient_phone = data['phone']
    payment_details = data['payment_details']

    send_invoice_email(recipient_email, payment_details)
    send_invoice_sms(recipient_phone, payment_details)

    return jsonify({"status": "success"})

def send_invoice_email(recipient_email, payment_details):
    message = Mail(
        from_email=config['sendgrid']['from_email'],
        to_emails=recipient_email,
        subject='Invoice for your payment',
        html_content=f"<strong>Thank you for your payment</strong><br>Details: {payment_details}"
    )
    sg.send(message)

def send_invoice_sms(recipient_phone, payment_details):
    message = twilio_client.messages.create(
        body=f"Thank you for your payment. Details: {payment_details}",
        from_=config['twilio']['from_phone'],
        to=recipient_phone
    )

app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
