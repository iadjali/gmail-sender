from pathlib import Path
from gmail_sender import send_email

send_email(
    fromaddr="you@gmail.com",
    toaddr="recipient@example.com",
    subject="Report + Screenshot",
    body="See attachments.",
    html=False,
    cc="manager@example.com,teamlead@example.com",
    bcc="audit@example.com",
    attachments=[
        Path("reports/daily.pdf"),
        Path("images/screenshot.png"),
    ],
)
