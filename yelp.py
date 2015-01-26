# -*- coding: utf-8 -*-
"""
Yelp API v2.0 code sample.
This program demonstrates the capability of the Yelp API version 2.0
by using the Search API to query for businesses and the Business API 
to query additional information about the results from the search query.
Please refer to http://www.yelp.com/developers/documentation for the API documentation.
This program requires the Python oauth2 library, which you can install via:
`pip install oauth2==1.0`.
"""

import argparse
import json
import pprint
import sys
import urllib
import urllib2

import oauth2

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = '345+Chambers+St,+New+York,+NY+10282'
SEARCH_LIMIT = 5
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = 'f1PkccB6x_aTd-Kf6WcHWg'
CONSUMER_SECRET = 'uy-E-8vbbS6jgYoe1PiiUnjKBNE'
TOKEN = 'Z8ZWhOb7nyy3iMFaQE0Dh7BPyQhEGj6B'
TOKEN_SECRET = 'aYPH8mA4AGFryCPUqQ42nH5MeJY'

def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
    host (str): The domain host of the API.
    path (str): The path of the API after the domain.
    url_params (dict): An optional set of query parameters in the request.
    Returns:
    dict: The JSON response from the request.
    Raises:
    urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, path)
    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)
    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    print 'Querying {0} ...'.format(url)
    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()
    return response


def search(term, limit, sort):
    """Query the Search API by a search term and location.
    Args:
    term (str): The search term passed to the API.
    location (str): The search location passed to the API.
    Returns:
    dict: The JSON response from the request.
    """
    url_params = {
        'term': term.replace(' ', '+'),
        'location': DEFAULT_LOCATION, #.replace(' ', '+'),
        'limit': limit,
        'sort': sort #a number from 0 to 2
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)


def get_business(business_id):
    """Query the Business API by a business ID.
    Args:
    business_id (str): The ID of the business to query.
    Returns:
    dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id
    return request(API_HOST, business_path)

#TAKEN AND MODIFIED FROM https://github.com/Yelp/yelp-api/blob/master/v2/python/sample.py
