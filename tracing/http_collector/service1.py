from loguru import logger
from flask import Flask, request

app = Flask(__name__)


from py_zipkin.zipkin import zipkin_span, ZipkinAttrs

import requests
import time

def http_transport(encoded_span):
    # The collector expects a thrift-encoded list of spans. Instead of
    # decoding and re-encoding the already thrift-encoded message, we can just
    # add header bytes that specify that what follows is a list of length 1.
    logger.debug("")
    ba = bytearray(b'\x0c\x00\x00\x00\x01')
    ba_span = bytearray (encoded_span)
    body =  ba.extend(ba_span)
    logger.debug("")
    requests.post(
        'http://192.168.10.127:9411/api/v1/spans',
        data=body,
        headers={'Content-Type': 'application/x-thrift'},
    )
    logger.debug("")

@zipkin_span(service_name='service1', span_name='service1_do_stuff')
def do_stuff():
    logger.debug("")
    time.sleep(5)
    return 'OK'

@app.route('/service1/')
def index():
    logger.debug("")
    with zipkin_span(
        service_name='service1',
        zipkin_attrs=ZipkinAttrs(
            trace_id=request.headers['X-B3-TraceID'],
            span_id=request.headers['X-B3-SpanID'],
            parent_span_id=request.headers['X-B3-ParentSpanID'],
            flags=request.headers['X-B3-Flags'],
            is_sampled=request.headers['X-B3-Sampled'],
        ),
        span_name='index_service1',
        transport_handler=http_transport,
        port=6000,
        sample_rate=100, #0.05, # Value between 0.0 and 100.0
    ):
        logger.debug("")
        do_stuff()
    logger.debug("")
    return 'OK', 200

if __name__ == '__main__':
    app.run(port=6000, debug=True)

