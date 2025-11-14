import os
import smtplib
import ssl
from email.message import EmailMessage
from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='site', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('site', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('site', path)

@app.route('/send-email', methods=['POST'])
def send_email():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    if not email or not message:
        return jsonify({'error': 'Email e messaggio richiesti'}), 400

    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    email_to = os.getenv('EMAIL_TO') or smtp_user
    email_from = os.getenv('EMAIL_FROM') or smtp_user

    body = f"Messaggio inviato dal sito\n\nNome: {name}\nEmail: {email}\n\n{message}"

    msg = EmailMessage()
    msg['Subject'] = f'Richiesta da sito GR Rosati - {name or email}'
    msg['From'] = email_from
    msg['To'] = email_to
    msg.set_content(body)

    try:
        # Use TLS
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls(context=context)
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(host='127.0.0.1', port=port, debug=True)
