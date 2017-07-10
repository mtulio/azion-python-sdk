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
#
# Azion API documentation:
# https://www.azion.com.br/developers/api/

# from __future__ import print_function
import os
import sys
import logging
import time

from .version import __version__
from service_api import APIService, ServiceException


logger = logging.getLogger(__name__)


class AzionAPI(APIService):
    """
        This is a abstraction layer of Azion API that handle many
        operations and abstract the use in python applications.
    """
    __version__ = __version__

    def __init__(self, url_api=None, token=None, token_type='session'):
        """
            Construct AzionAPI object to interact with API.

            :param str url_api: URL of Azion's API.
            :param str token: Session Token to interact with the API.
            :param str token_type: Type of token. In future we can use other ways.
        """

        if url_api is None:
            url_api = 'https://api.azion.net'

        self.routes = {
            'cdn_config': '/content_delivery/configurations'
        }
        self.status = {
            'exists': 1,
            'wrong_payload': 2,
            'ok': 200,
            'bad_request': 404,
            'not_found': 404,
            'token_expired': 403,
            'too_many_req': 429,
            'server_error': 500
        }

        # throtle defined by API - HTTP 429 https://www.azion.com.br/developers/api/
        self.throtle_limit_min = 20

        if token_type == 'session':
            if token is None:
                try:
                    token = os.getenv("AZION_TOKEN") or None
                except:
                    raise ('Unable to get Session token AZION_TOKEN from env')

        #TODO
        elif token_type == 'auth':
            if token is None:
                try:
                    token = os.getenv("AZION_BASE64") or None
                except:
                    raise ('Unable to get Base64 auth token AZION_BASE64 from env')

        # force to use session token
        APIService.__init__(self, url_api, token_sess=token)


    # AZION CDN Operations / abstraction
    # CDN abstraction
    def _cdn_origins_config(self, cdn_config):
        """
            Return CDN Origins configuration.

            :param str cdn_config: base CDN config to be get origins.
            :return: Return the Dict with CDN Origins configuration.
            :rtype : Dict
        """

        if isinstance(cdn_config, dict):
            path = '{:s}/{}/origins'.format(self.routes['cdn_config'], cdn_config['id'])
            cdn_config['origins'] = self.get(path)

        return cdn_config

    def _cdn_cache_config(self, cdn_config):
        """
            Return CDN Cache configuration.

            :param str cdn_config: base CDN config to be get cache settings.
            :return: Return the Dict with CDN Cache configuration.
            :rtype : Dict
        """

        if isinstance(cdn_config, dict):
            path = '{:s}/{}/cache_settings'.format(self.routes['cdn_config'], cdn_config['id'])
            cdn_config['cache_settings'] = self.get(path)

        return cdn_config

    def _cdn_rules_config(self, cdn_config):
        """
            Return CDN Rules Engine configuration.

            :param str cdn_config: base CDN config to be get rules_engine.
            :return: Return the Dict with CDN Rules Engine configuration.
            :rtype : Dict
        """

        if isinstance(cdn_config, dict):
            path = '{:s}/{}/rules_engine'.format(self.routes['cdn_config'], cdn_config['id'])
            cdn_config['rules_engine'] = self.get(path)

        return cdn_config

    def _cdn_config_expand(self, cdn_config):
        """
            Discovery and expand CDN configuration. This operation should be
            done because current API does not return all CDN config in base
            request.

            :param str cdn_config: CDN dict to be expaended.
            :return: Return the Dict with CDN configuration.
            :rtype : Dict

            Expand all config in a dict. The config available are:
            * digital_certificate
            * origin - /content_delivery/configurations/:conf_id/origins
            * cache_settings - /content_delivery/configurations/:conf_id/cache_settings
            * rules_engine /content_delivery/configurations/:conf_id/rules_engine
        """

        if not isinstance(cdn_config, dict):
            return {}

        cdn_config = self._cdn_origins_config(cdn_config)
        cdn_config = self._cdn_cache_config(cdn_config)
        cdn_config = self._cdn_rules_config(cdn_config)

        return cdn_config

    def _cdn_config_callback(self, cdn_config, option='all'):
        """
            Route operation to return the desired CDN configuration.

            :param str cdn_config: Dict to be routed.
            :param str option: Trigger to route function.
            :return: Return the Dict with CDN configuration.
            :rtype : Dict
        """

        if option == 'all':
            return self._cdn_config_expand(cdn_config)
        elif option == 'origin':
            return self._cdn_origins_config(cdn_config)
        elif option == 'cache':
            return self._cdn_cache_config(cdn_config)
        elif option == 'rules':
            return self._cdn_rules_config(cdn_config)

    def get_cdn_config(self, option='all', cdn_id=None, cdn_name=None):
        """
            Return the CDN configuration, can lookup by ID or Name.

            :param str option: The operation to be done. Could be all, origin,
                cache and rules.
            :param int cdn_id: CDN ID to get the configuration.
            :param str cdn_name: CDN Name to get the configuration.
            :return: Return the Dict with configuration when cdn_id or cdn_name
                is provided. When leaves default values of arguments, all the
                configuration is returned in array format.
            :rtype : Dict
        """

        try:
            status = self.status['not_found']
            cfg = {}
            if not self.api_has_session():
                self.init_api()

            if cdn_id is not None:
                path = '{:s}/{:d}'.format(self.routes['cdn_config'], cdn_id)
                c = self.get(path)
                if not isinstance(c, dict):
                    return cfg_all, 401

                if 'id' in c:
                    return (self._cdn_config_callback(c, option=option),
                            self.status['ok'])

                return cfg, status

            elif cdn_name is not None:
                cfg_all = self.get(self.routes['cdn_config'])
                if not isinstance(cfg_all, list):
                    return cfg_all, 401

                for c in cfg_all:
                    if c['name'] == cdn_name:
                        return (self._cdn_config_callback(c, option=option),
                                self.status['ok'])

                return cfg, status

            else:
                cfg = []
                cfg_all = self.get(self.routes['cdn_config'])
                if not isinstance(cfg_all, list):
                    return cfg_all, 401

                count = 1
                for c in cfg_all:
                    if count > (self.throtle_limit_min - 3):
                        #print ("Avoiding Throtle {} of {}. Waiting 50s".format(count,
                        #                                self.throtle_limit_min))
                        time.sleep(50)
                        count = 0

                    cfg.append(self._cdn_config_expand(c))
                    count += 3

                if len(cfg) > 0:
                    status = self.status['ok']

                return cfg, status

        except ServiceException as e:
            return {'{}'.format(e)}, self.status['server_error']
