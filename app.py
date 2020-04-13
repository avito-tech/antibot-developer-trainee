import falcon
from collections import deque
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from ipaddress import IPv4Address
from wsgiref import simple_server

import config


class CachedNetwork:
    def __init__(self, limiting_req_n: int):
        self.last_ban = datetime.min
        self.responses = deque([datetime.min], maxlen=limiting_req_n)


class AntiBotFilter:
    def __init__(self, limiting_req_n: int, limiting_period: timedelta, ip_mask: IPv4Address):
        def cached_network_init():
            return CachedNetwork(limiting_req_n)

        self._limiting_period = limiting_period
        self._ip_mask = ip_mask
        self._ip_networks = defaultdict(cached_network_init)

    def process_request(self, req, resp):
        ip_address = IPv4Address(req.access_route[0])
        req_time = datetime.now()
        nw_address = '{ip_address}/{ip_mask}'.format(ip_address=ip_address.compressed, ip_mask=self._ip_mask)
        limiting_req_time = self._ip_networks[nw_address].responses[0]
        limiting_req_timedelta = req_time - limiting_req_time
        self._ip_networks[nw_address].responses.append(req_time)
        if limiting_req_timedelta < self._limiting_period:
            raise falcon.HTTPTooManyRequests()


class ExampleResource:
    def on_post(self, req, resp):
        pass


def create_app(limiting_req_n, limiting_period, ip_mask):
    anti_bot_filter = AntiBotFilter(
        limiting_req_n=limiting_req_n,
        limiting_period=limiting_period,
        ip_mask=ip_mask
    )

    resource = ExampleResource()

    api = falcon.API(middleware=[anti_bot_filter])
    api.add_route('/', resource)
    return api


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 9000
    created_add = create_app(
        limiting_req_n=config.LIMITING_REQ_N,
        limiting_period=config.LIMITING_PERIOD,
        ip_mask=config.IP_MASK
    )
    httpd = simple_server.make_server(host, port, create_app())
    httpd.serve_forever()
