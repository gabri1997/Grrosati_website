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
    # Destination: prefer explicit EMAIL_TO env var, then SMTP_USER, otherwise fallback
    email_to = os.getenv('EMAIL_TO') or smtp_user or 'grrosati@libero.it'
    # From address: prefer EMAIL_FROM, then SMTP_USER, otherwise use a generic noreply
    email_from = os.getenv('EMAIL_FROM') or smtp_user or 'noreply@grrosati.local'

    body = f"Messaggio inviato dal sito\n\nNome: {name}\nEmail: {email}\n\n{message}"

    msg = EmailMessage()
    msg['Subject'] = f'Richiesta da sito GR Rosati - {name or email}'
    msg['From'] = email_from
    msg['To'] = email_to
    msg.set_content(body)

    # If SMTP is configured, try to send. If not, fall back to saving the message to a local outbox file.
    if smtp_host:
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
            # On failure, save to local outbox for inspection and return the error
            try:
                outdir = os.path.join(os.getcwd(), 'outbox')
                os.makedirs(outdir, exist_ok=True)
                fname = os.path.join(outdir, f"message_{int(__import__('time').time())}.eml")
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(msg.as_string())
            except Exception:
                pass
            return jsonify({'error': str(e), 'saved_to': fname}), 500
    else:
        # SMTP not configured: save the message to a local outbox directory so it can be retrieved.
        outdir = os.path.join(os.getcwd(), 'outbox')
        os.makedirs(outdir, exist_ok=True)
        fname = os.path.join(outdir, f"message_{int(__import__('time').time())}.eml")
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(msg.as_string())
            return jsonify({'ok': True, 'saved_to': fname})
        except Exception as e:
            return jsonify({'error': 'SMTP non configurato e scrittura su file fallita: ' + str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(host='127.0.0.1', port=port, debug=True)
