import logging
from smtplib import SMTPAuthenticationError, SMTPDataError, SMTPRecipientsRefused
from unittest.mock import patch

import pytest

from app import send_confirmation_email, send_password_reset_email
from models import User, db
from test_app import create_user


SENDERS = [send_confirmation_email, send_password_reset_email]


@pytest.mark.parametrize("send_email", SENDERS)
@pytest.mark.parametrize("failure", ["recipient", "authentication", "message"])
def test_mail_failure_does_not_log_private_details(app, caplog, send_email, failure):
    user_id = create_user(app)
    errors = {
        "recipient": SMTPRecipientsRefused(
            {"user@example.com": (550, b"private_recipient_detail")}
        ),
        "authentication": SMTPAuthenticationError(
            535, b"private_authentication_detail"
        ),
        "message": SMTPDataError(
            554, b"private_message_detail reset-token-marker code-marker"
        ),
    }
    error = errors[failure]
    with (
        app.test_request_context(),
        caplog.at_level(logging.ERROR, logger=app.logger.name),
        patch("app.mail_is_configured", return_value=True),
        patch("app.mail.send", side_effect=error) as send,
    ):
        assert send_email(db.session.get(User, user_id)) is False
        send.assert_called_once()
    assert type(error).__name__ in caplog.text
    for marker in ("user@example.com", "private_", "reset-token-marker", "code-marker"):
        assert marker not in caplog.text
    assert caplog.records
    assert all(record.exc_info is None for record in caplog.records)


@pytest.mark.parametrize("send_email", SENDERS)
def test_successful_mail_still_sends_to_user_without_logging_content(
    app, caplog, send_email
):
    user_id = create_user(app)
    with (
        app.test_request_context(),
        caplog.at_level(logging.INFO, logger=app.logger.name),
        patch("app.mail_is_configured", return_value=True),
        patch("app.mail.send") as send,
    ):
        assert send_email(db.session.get(User, user_id)) is True
        send.assert_called_once()
        message = send.call_args.args[0]
        assert message.recipients == ["user@example.com"]
        assert message.html
    assert "user@example.com" not in caplog.text
    assert message.html not in caplog.text
    assert "/reset_password/" not in caplog.text


@pytest.mark.parametrize("send_email", SENDERS)
def test_unconfigured_mail_is_not_sent(app, send_email):
    user_id = create_user(app)
    with (
        app.test_request_context(),
        patch("app.mail_is_configured", return_value=False),
        patch("app.mail.send") as send,
    ):
        user = db.session.get(User, user_id)
        assert send_email(user) is False
        send.assert_not_called()
        assert user.email_code_hash is None
