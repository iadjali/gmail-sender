
from __future__ import annotations

import argparse
import base64
import mimetypes
import os
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Least-privilege scope for sending only

class GmailSendError(Exception):
    """Raised when sending via Gmail API fails."""
    pass


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _secrets_dir() -> Path:
    """
    Resolve secrets directory.
    Override with env var GMAIL_SECRETS_DIR if desired.
    """
    d = Path(os.getenv("GMAIL_SECRETS_DIR", Path(__file__).resolve().parent / ".secrets"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _paths() -> tuple[Path, Path]:
    base = _secrets_dir()
    return base / "token.json", base / "credentials.json"


def _authorize(scopes: list[str]) -> Credentials:
    token_path, creds_path = _paths()
    creds: Optional[Credentials] = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(
                    f"Missing credentials file at {creds_path}.\n"
                    "Download the OAuth client (Desktop) JSON from Google Cloud Console "
                    "and place it there. See README for setup."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), scopes)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds



def get_service(scopes: list[str] | None = None):
    """Return an authorized Gmail API service instance."""
    if scopes is None:
        scopes = SCOPES
    creds = _authorize(scopes)
    return build("gmail", "v1", credentials=creds)



def _attach_files(msg: EmailMessage, attachments: Sequence[Path]) -> None:
    for p in attachments:
        p = Path(p)
        if not p.is_file():
            raise FileNotFoundError(f"Attachment not found: {p}")
        ctype, encoding = mimetypes.guess_type(p.name)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with p.open("rb") as f:
            data = f.read()
        msg.add_attachment(
            data,
            maintype=maintype,
            subtype=subtype,
            filename=p.name,
        )


def send_email(
    fromaddr: str,
    toaddr: str,
    subject: str,
    body: str,
    *,
    html: bool = False,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    attachments: Optional[Sequence[Path]] = None,
    service=None,
) -> dict:
    """Create and send an email message. Returns Gmail API message resource."""
    creds = _authorize(SCOPES)

    try:
        service = service or get_service()
        message = EmailMessage()

        if html:
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        message["To"] = toaddr
        message["From"] = fromaddr
        message["Subject"] = subject
        if cc:
            message["Cc"] = cc
        if bcc:
            message["Bcc"] = bcc

        if attachments:
            _attach_files(message, attachments)

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        create_message = {"raw": encoded_message}

        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        return send_message
    except HttpError as error:
        raise GmailSendError(f"Gmail API error: {error}") from error


def main() -> None:
    parser = argparse.ArgumentParser(description="Send an email via Gmail API (OAuth).")
    parser.add_argument("--from", dest="fromaddr", required=True, help="From address (your Gmail).")
    parser.add_argument("--to", dest="toaddr", required=True, help="Recipient address.")
    parser.add_argument("--subject", required=True, help="Email subject.")

    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--body", help="Plain text (or HTML if --html) message body.")
    g.add_argument("--body-file", help="Path to file to use as body.")

    parser.add_argument("--html", action="store_true", help="Interpret body as HTML.")
    parser.add_argument("--cc", help="Comma-separated CC addresses.")
    parser.add_argument("--bcc", help="Comma-separated BCC addresses.")
    parser.add_argument(
        "--attach",
        action="append",
        default=[],
        help="Path to file to attach. Repeat flag to add multiple.",
    )
    args = parser.parse_args()

    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else args.body
    resp = send_email(
        args.fromaddr,
        args.toaddr,
        args.subject,
        body,
        html=args.html,
        cc=args.cc,
        bcc=args.bcc,
        attachments=[Path(p) for p in args.attach],
    )
    print(f"Message sent. ID: {resp.get('id')}")


if __name__ == "__main__":
    main()
