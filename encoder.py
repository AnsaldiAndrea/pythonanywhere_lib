"""module for text encoding/decoding to/from base64 """
import base64


def encode(string):
    """encode string to base64"""
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


def decode(string):
    """decode string from base64"""
    return base64.b64decode(string).decode('utf-8')
