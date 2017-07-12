#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017 MTOps All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# from __future__ import print_function

import json
import logging
import requests
from requests.structures import CaseInsensitiveDict
from .version import __version__

logger = logging.getLogger(__name__)

def _remove_null_values(dictionary):
    if isinstance(dictionary, dict):
        return dict([(k, v) for k, v in dictionary.items() if v is not None])
    return dictionary


def _cleanup_param_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return value


def _cleanup_param_values(dictionary):
    if isinstance(dictionary, dict):
        return dict(
            [(k, _cleanup_param_value(v)) for k, v in dictionary.items()])
    return dictionary


class ServiceException(Exception):
    pass


class ServiceInvalidArgument(ServiceException):
    pass


class APIService(object):
    """ Polymorphic class of API REST Service. """
    # __version__ = __version__

    def __init__(self, url_api, token_auth=None, token_sess=None,
                 username=None, password=None):
        """
            You can choose in setup initial authentication using username and
            password, or setup with Authorization HTTP token. If token_auth is set,
            username and password credentials must be ignored.
        """
        # self.__version__ = __version__
        self.url = url_api

        self.token_auth = token_auth
        self.token_sess = token_sess

        self.username = username
        self.password = password


    def set_token_auth(self, token_auth):
        if token_auth == 'YOUR AUTH TOKEN':
            token_auth = None

        self.token_auth = token_auth

    def set_uri(self, uri):
        self.uri = uri

    def get_version(self):
        return self.__version__

    def get_config(self):
        config = {
            'url': self.url,
            'token_auth': self.token_auth,
            'token_sess': self.token_sess,
            'username': self.username,
            'password': self.password
        }
        return config

    """
    Session Token (#TODO)
    """
    def api_has_session(self):
        """ #TODO: Ping session to check if token is not expired """
        return True

    """ Request """
    def request(self, method, url, headers={}, params=None, data=None,
                files=None, data_json=None, accept_json=True, json_ver=None,
                ua_default=True, **kwargs):
        """
        Make a request to Rest API.
        @return Return response object.
        """

        full_url = '%s/%s' % (self.url, url.strip('/'))
        input_headers = _remove_null_values(headers) if headers else {}

        if ua_default:
            headers = CaseInsensitiveDict(
                {'user-agent': 'azion-sdk-python-' + __version__})

        if accept_json:
            if json_ver:
                h_accept = 'application/json; version={}'.format(json_ver)
            else:
                h_accept = 'application/json'
            headers.update({"accept": h_accept})

        headers.update({"Content-Type": "application/json"})

        try:
            #if self.session is None:
            #    self.set_session_token()
            if self.token_sess is not None:
                headers.update({'Authorization':  "Token {}".format(self.token_sess)})

        except ServiceException as e:
            raise ServiceException("Unable to get Session token. ERROR: {}".format(e))

        headers.update(input_headers)

        # Remove keys with None values
        params = _remove_null_values(params)
        params = _cleanup_param_values(params)
        data = _remove_null_values(data)
        files = _remove_null_values(files)

        try:
            response = requests.request(method=method, url=full_url,
                                        headers=headers, params=params,
                                        data=data, json=data_json, **kwargs)
        except Exception:
            logger.error("ERROR requesting uri(%s) payload(%s)" % (url, data))
            raise

        return response

    """ Generic Items methods """
    # [C]REATE - Create an Item
    def create(self, path, payload=None, payload_json=None, json_ver=None):
        """ Create an Item. """

        response = self.request('POST', path, data=payload,
                                json_ver=json_ver, data_json=payload_json)

        if response.status_code >= 200 and response.status_code < 500:
            return response.json()

        # 5xx is returning wrong answer
        return { 'error': '{}'.format(response.status_code)}

    # [R]EAD - GET config
    def get(self, path, json_ver=None):
        """ Return all content of Path in JSON format. """

        response =  self.request('GET', path, json_ver=json_ver)

        if response.status_code >= 200 and response.status_code < 500:
            return response.json()

        return { 'error': '{} {}'.format(response.status_code,
                                              response.text)}

    # [U]PDATE - config
    ## Update fields
    def update(self, path, payload):
        """ #TODO: Update an object Item. """

        response = self.request('PATCH', path, data=payload)
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()

        return { 'error': '{:d}: {:s}'.format(response.status_code,
                                              response.text)}

    ## Override config
    def override(self, path, payload):
        """ #TODO: Update an object Item. """

        response = self.request('PUT', path, data=payload)
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()

        return { 'error': '{:d}: {:s}'.format(response.status_code,
                                              response.text)}

    # [D]ELETE an Item
    def delete(self, path, force_purge=False):
        """ #TODO: Delete an object Item. """

        response = self.request('DELETE', path)
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()

        return { 'error': '{:d}: {:s}'.format(response.status_code,
                                              response.text)}
