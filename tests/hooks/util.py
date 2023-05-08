import router_log_preprocessor.domain
import router_log_preprocessor.util.rfc3164_parser

RECORD = router_log_preprocessor.domain.LogRecord(
    facility=1,
    severity=5,
    timestamp=router_log_preprocessor.util.rfc3164_parser.timestamp_to_datetime(
        "Feb", "2", "13", "02", "51"
    ),
    hostname="GT-AX11000-ABCD-1234567-E",
    process="wlceventd",
    process_id=None,
    message="Not relevant for testing",
)

MESSAGE = router_log_preprocessor.domain.WlcEventModel(
    location="wl0.1",
    mac_address=router_log_preprocessor.domain.MAC("AB:CD:EF:01:23:45"),
    status=0,
    event=router_log_preprocessor.domain.WlcEvent.DEAUTH_IND,
    rssi=0,
    reason="N/A",
)