from loguru import logger
from flask import Flask
from flask import request

from py_zipkin.util import generate_random_64bit_string
from py_zipkin.zipkin import create_http_headers_for_new_span
from py_zipkin.zipkin import ZipkinAttrs
from py_zipkin.zipkin import zipkin_span

import os
import requests

app = Flask(__name__)

TRACE_HEADERS_TO_PROPAGATE = [
    'X-Ot-Span-Context',
    'X-Request-Id',
    'X-B3-TraceId',
    'X-B3-SpanId',
    'X-B3-ParentSpanId',
    'X-B3-Sampled',
    'X-B3-Flags'
]

def http_transport(encoded_span):
    logger.debug(f"")
    requests.post(
        'http://192.168.10.127:9411/api/v1/spans',
        data=encoded_span,
        headers={'Content-Type': 'application/x-thrift'},
    )
    logger.debug(f"")

def extract_zipkin_attrs(headers):
    logger.debug(f"headers:{headers}")
    return ZipkinAttrs(
            headers['X-B3-TraceId'],
            generate_random_64bit_string(),
            headers['X-B3-SpanId'],
            headers.get('X-B3-Flags', ''),
            headers['X-B3-Sampled'],
            )

@app.route('/')
def trace():
    logger.debug(f"")
    headers = {}
    if not os.getenv('SKIP_INSERVICE_PROPAGATION', False):
        for header in TRACE_HEADERS_TO_PROPAGATE:
            if header in request.headers:
                headers[header] = request.headers[header]

    with zipkin_span(
            service_name='service{}'.format("1"),
            span_name='service',
            transport_handler=http_transport,
            port=4000,   # int(os.environ['PORT']),
            zipkin_attrs=extract_zipkin_attrs(request.headers)):
        if int("1") == 1 :
            requests.get("http://127.0.0.1:6000/service1/", headers=headers)

        return ('Hello from service {}!\n'.format("1"))

@app.route('/2')
def trace2():
    logger.debug(f"")
    headers = {}
    if not os.getenv('SKIP_INSERVICE_PROPAGATION', False):
        for header in TRACE_HEADERS_TO_PROPAGATE:
            if header in request.headers:
                headers[header] = request.headers[header]

    with zipkin_span(
            service_name='service{}'.format("1"),
            span_name='service',
            transport_handler=http_transport,
            port=int(os.environ['PORT']),
            zipkin_attrs=extract_zipkin_attrs(request.headers)):
        if int("1") == 1 :
            requests.get("http://127.0.0.1:6000/service1/", headers=headers)

        return ('Hello from service {}!\n'.format("1"))

if __name__ == "__main__":
    logger.debug(f"")
    app.run(host='0.0.0.0', port=4000, debug=True)