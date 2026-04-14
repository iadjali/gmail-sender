from __future__ import annotations

import argparse
import base64
import logging
import mimetypes
import os
import re
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Least-privilege scope for sending only


class GmailSendError(Exception):
    """Raised when sending via Gmail API fails."""

    pass


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _validate_email(addr: str) -> None:
    """Validate email address format."""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(pattern, addr):
        raise ValueError(f"Invalid email address: {addr}")


def _validate_emails(emails: str) -> None:
    """Validate comma-separated email addresses."""
    for email in emails.split(","):
        email = email.strip()
        if email:
            _validate_email(email)


def _secrets_dir() -> Path:
    """
    Resolve secrets directory.
    Override with env var GMAIL_SECRETS_DIR if desired.
    """
    d = Path(
        os.getenv("GMAIL_SECRETS_DIR", Path(__file__).resolve().parent / ".secrets")
    )
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
    service: Optional[Resource] = None,
) -> dict:
    """
    Create and send an email message via Gmail API.

    Args:
        fromaddr: Sender's Gmail address
        toaddr: Recipient email address
        subject: Email subject line
        body: Email body (plain text or HTML)
        html: If True, body is interpreted as HTML
        cc: Comma-separated CC addresses (optional)
        bcc: Comma-separated BCC addresses (optional)
        attachments: Sequence of Path objects to attach
        service: Reusable Gmail API service (optional)

    Returns:
        Gmail API message resource dict with 'id' key

    Raises:
        GmailSendError: If Gmail API call fails
        FileNotFoundError: If attachment or credentials file missing
        ValueError: If email addresses are invalid
    """

    try:
        # Validate email addresses
        _validate_email(fromaddr)
        _validate_email(toaddr)
        if cc:
            _validate_emails(cc)
        if bcc:
            _validate_emails(bcc)

        logger.info(
            f"Sending email from {fromaddr} to {toaddr} with subject '{subject}'"
        )
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
        logger.info(f"Email sent successfully. Message ID: {send_message.get('id')}")
        return send_message
    except HttpError as error:
        logger.error(f"Gmail API error: {error}")
        raise GmailSendError(f"Gmail API error: {error}") from error


def main() -> None:
    parser = argparse.ArgumentParser(description="Send an email via Gmail API (OAuth).")
    parser.add_argument(
        "--from", dest="fromaddr", required=True, help="From address (your Gmail)."
    )
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

    body = (
        Path(args.body_file).read_text(encoding="utf-8")
        if args.body_file
        else args.body
    )
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
