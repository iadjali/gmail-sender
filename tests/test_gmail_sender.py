from unittest.mock import Mock, patch

import pytest

from gmail_sender import (
    GmailSendError,
    _attach_files,
    _validate_email,
    _validate_emails,
    send_email,
)


class TestEmailValidation:
    def test_valid_email(self):
        _validate_email("test@example.com")
        _validate_email("user.name+tag@domain.co.uk")

    def test_invalid_email(self):
        with pytest.raises(ValueError, match="Invalid email address"):
            _validate_email("invalid-email")
        with pytest.raises(ValueError, match="Invalid email address"):
            _validate_email("test@")
        with pytest.raises(ValueError, match="Invalid email address"):
            _validate_email("@example.com")

    def test_valid_emails_comma_separated(self):
        _validate_emails("a@example.com, b@example.com")
        _validate_emails("single@example.com")

    def test_invalid_emails_comma_separated(self):
        with pytest.raises(ValueError, match="Invalid email address"):
            _validate_emails("valid@example.com, invalid")


class TestAttachmentHandling:
    def test_attach_files_file_not_found(self, tmp_path):
        from email.message import EmailMessage

        msg = EmailMessage()
        nonexistent = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            _attach_files(msg, [nonexistent])

    def test_attach_files_success(self, tmp_path):
        from email.message import EmailMessage

        msg = EmailMessage()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        _attach_files(msg, [test_file])

        # Check that attachment was added
        assert len(msg.get_payload()) == 1
        attachment = msg.get_payload()[0]
        assert attachment.get_filename() == "test.txt"


class TestSendEmail:
    @patch("gmail_sender.get_service")
    def test_send_email_basic(self, mock_get_service):
        mock_service = Mock()
        mock_message = Mock()
        mock_message.get.return_value = "test-id"
        mock_service.users().messages().send().execute.return_value = mock_message
        mock_get_service.return_value = mock_service

        result = send_email(
            fromaddr="sender@gmail.com",
            toaddr="recipient@example.com",
            subject="Test",
            body="Test body",
        )

        assert result == mock_message

    @patch("gmail_sender.get_service")
    def test_send_email_with_attachments(self, mock_get_service, tmp_path):
        mock_service = Mock()
        mock_message = Mock()
        mock_message.get.return_value = "test-id"
        mock_service.users().messages().send().execute.return_value = mock_message
        mock_get_service.return_value = mock_service

        test_file = tmp_path / "attachment.txt"
        test_file.write_text("attachment content")

        result = send_email(
            fromaddr="sender@gmail.com",
            toaddr="recipient@example.com",
            subject="Test with attachment",
            body="Test body",
            attachments=[test_file],
        )

        assert result == mock_message

    @patch("gmail_sender.get_service")
    def test_send_email_api_error(self, mock_get_service):
        from googleapiclient.errors import HttpError

        mock_service = Mock()
        mock_service.users().messages().send().execute.side_effect = HttpError(
            resp=Mock(status=400), content=b'{"error": "test error"}'
        )
        mock_get_service.return_value = mock_service

        with pytest.raises(GmailSendError, match="Gmail API error"):
            send_email(
                fromaddr="sender@gmail.com",
                toaddr="recipient@example.com",
                subject="Test",
                body="Test body",
            )

    def test_send_email_invalid_from_email(self):
        with pytest.raises(ValueError, match="Invalid email address"):
            send_email(
                fromaddr="invalid-email",
                toaddr="recipient@example.com",
                subject="Test",
                body="Test body",
            )

    def test_send_email_invalid_to_email(self):
        with pytest.raises(ValueError, match="Invalid email address"):
            send_email(
                fromaddr="sender@gmail.com",
                toaddr="invalid-email",
                subject="Test",
                body="Test body",
            )

    def test_send_email_invalid_cc_email(self):
        with pytest.raises(ValueError, match="Invalid email address"):
            send_email(
                fromaddr="sender@gmail.com",
                toaddr="recipient@example.com",
                subject="Test",
                body="Test body",
                cc="invalid-email",
            )
