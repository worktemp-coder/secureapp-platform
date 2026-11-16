import logging

from flask import has_request_context, request
from prometheus_client import Counter

AUDIT_LOGGER = logging.getLogger("secureapp.audit")

LOGIN_COUNTER = Counter(
    "secureapp_login_total",
    "Login attempts grouped by outcome.",
    ["outcome"],
)
RATE_LIMIT_COUNTER = Counter(
    "secureapp_rate_limited_total",
    "Requests rejected by the rate limiter.",
)
ACCESS_DENIED_COUNTER = Counter(
    "secureapp_access_denied_total",
    "Requests denied by authorization checks.",
    ["reason"],
)


def audit(event, outcome, **fields):
    payload = {
        "event": event,
        "outcome": outcome,
    }
    payload.update(fields)

    if has_request_context():
        payload["remote_addr"] = request.remote_addr
        payload["path"] = request.path
        user_agent = request.headers.get("User-Agent", "")
        payload["user_agent"] = user_agent[:160]

    AUDIT_LOGGER.info("audit_event", extra=payload)
