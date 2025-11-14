# Ambiente virtuale

Questo repository contiene un ambiente virtuale Python creato con `venv`.

Come attivare (bash):

```bash
# dalla cartella del progetto
source .venv/bin/activate

# verificare la versione di Python e pip
python -V
pip -V
```

Installare dipendenze (se presenti):

```bash
pip install -r requirements.txt
```

Per uscire dall'ambiente virtuale:

```bash
deactivate
```

Se vuoi che io aggiunga dipendenze iniziali, dimmi quali pacchetti vuoi includere e aggiorno `requirements.txt` e li installo.

## Eseguire l'app di sviluppo (backend + sito statico)

1. Attiva l'ambiente virtuale (bash):

```bash
source .venv/bin/activate
```

2. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

3. Copia `.env.example` in `.env` e imposta le variabili SMTP (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_TO, EMAIL_FROM).

4. Avvia il server:

```bash
.venv/bin/python app.py
```

5. Apri `http://127.0.0.1:5000` nel browser. Il form nella sidebar invierà una richiesta a `/send-email`.

Nota: questo server è pensato per sviluppo/uso locale. Per produzione considera di usare un server WSGI (gunicorn/uvicorn) dietro a un reverse-proxy e di proteggere le credenziali SMTP.
