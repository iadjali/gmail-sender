
# gmail-sender

A minimal, safe command-line utility to send email via the Gmail API using OAuth 2.0.  
No secrets are committed; OAuth tokens and credentials live in a local `.secrets/` directory
(or a custom folder via `GMAIL_SECRETS_DIR`).

## Requirements
- Python 3.11+
- Google Cloud OAuth **Desktop** Client credentials JSON

## Install
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

## Configure OAuth
1. In Google Cloud Console, create an **OAuth client ID** of type **Desktop**.
2. Download the client JSON and place it at:
   ```
   ./.secrets/credentials.json
   ```
   (The `.secrets/` folder is created automatically on first run. You can also set
   `GMAIL_SECRETS_DIR=/custom/path` to keep secrets elsewhere.)
3. On the first run, a browser window opens for consent. A `token.json` is saved to `.secrets/`.

## Usage

### Plain text email
```bash
python gmail_sender.py   --from you@gmail.com   --to recipient@example.com   --subject "Hello"   --body "Hi from Gmail API!"
```

### HTML email
```bash
python gmail_sender.py   --from you@gmail.com   --to recipient@example.com   --subject "Hello"   --body-file ./examples/hello.html   --html
```

### With attachments (one or more)
```bash
python gmail_sender.py   --from you@gmail.com   --to recipient@example.com   --subject "Report + screenshot"   --body "See attachments."   --attach ./reports/daily.pdf   --attach ./images/screenshot.png
```

### Optional headers
- `--cc "a@ex.com,b@ex.com"`
- `--bcc "x@ex.com"`


## Programmatic usage (import in your app)


## Programmatic tips

- **Reusable service**: For many sends in a batch, reuse a single Gmail API service:
  ```python
  from gmail_sender import send_email, get_service

  service = get_service()
  for r in ["a@example.com", "b@example.com"]:
      send_email(
          fromaddr="you@gmail.com",
          toaddr=r,
          subject="Hello",
          body=f"Hi {r}!",
          service=service,  # reuse the same client
      )
  ```

- **Library-style errors**: `send_email()` raises `GmailSendError` on failures:
  ```python
  from gmail_sender import send_email, GmailSendError

  try:
      send_email(
          fromaddr="you@gmail.com",
          toaddr="recipient@example.com",
          subject="Hi",
          body="Test",
      )
  except GmailSendError as e:
      print("Failed to send:", e)
  ```


Examples are provided in the [`examples/`](./examples) folder:

- `examples/app_send_text.py` – minimal plain text send
- `examples/app_send_html.py` – HTML body
- `examples/app_send_with_cc_bcc_attachments.py` – CC, BCC, and multiple attachments
- `examples/app_custom_secrets_dir.py` – put OAuth files outside the repo with `GMAIL_SECRETS_DIR`
- `examples/app_bulk_simple.py` – simple bulk loop
- `examples/app_with_error_handling.py` – catch and report errors
- `examples/worker_task.py` – sample function you could call from a web/job handler

Minimal example:
```python
from gmail_sender import send_email

send_email(
    fromaddr="you@gmail.com",
    toaddr="recipient@example.com",
    subject="Hello",
    body="Hi from my app!",
    html=False,
)
```

## Safety
- `.secrets/` (and `credentials.json` / `token.json`) are **git-ignored**. Never commit them.
- If you accidentally commit secrets, immediately revoke the OAuth credentials in Google Cloud,
  delete the leaked token, rotate keys, and rewrite history before pushing again.

## Troubleshooting
- **invalid_grant**: Remove `.secrets/token.json` and re-authenticate.
- **403 insufficientPermissions**: Ensure scope is exactly `gmail.send`, delete token and re-auth.
- **Desktop app blocked**: Verify the OAuth client type is **Desktop**.

## License
MIT
