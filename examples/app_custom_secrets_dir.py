import os
from gmail_sender import send_email

# Keep OAuth files outside the project tree
os.environ["GMAIL_SECRETS_DIR"] = "/opt/app-secrets/gmail"

send_email(
    fromaddr="you@gmail.com",
    toaddr="recipient@example.com",
    subject="Hello from a container",
    body="Secrets are outside the repo — nice.",
)
