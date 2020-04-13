from datetime import timedelta
from ipaddress import IPv4Address

LIMITING_REQ_N = 100
LIMITING_PERIOD = timedelta(minutes=2)
IP_MASK = IPv4Address('255.255.255.0')
