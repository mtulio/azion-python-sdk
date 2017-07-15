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

from service_api import APIService, ServiceException
from .version import __version__
import sample

logger = logging.getLogger(__name__)


def lookup_id_from_name(name, cfg):
    """
        Return ID key from an name in an config dict.
        :param str name: The string to lookup in an key 'name'.
        :param list cfg: The list of dicts to lookup 'id' from an 'name'.
        :return: The ID match with the 'name' string, or 0 if not found.
        :rtype : Integer
    """
    try:
        cfg_id = filter(lambda c: c['name'] == name, cfg)[0]['id']
    except:
        cfg_id = 0

    return cfg_id


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
            :param str token_type: Type of token.
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

        # API throtle - HTTP 429 https://www.azion.com.br/developers/api/
        self.throtle_limit_min = 20

        if token_type == 'session':
            if token is None:
                try:
                    token = os.getenv("AZION_TOKEN") or None
                except:
                    raise ('Unable to get Session token from env AZION_TOKEN')

        #TODO
        elif token_type == 'auth':
            if token is None:
                try:
                    token = os.getenv("AZION_BASE64") or None
                except:
                    raise ('Unable to get Base64 token from env AZION_BASE64')

        # force to use session token
        APIService.__init__(self, url_api, token_sess=token)


    # AZION CDN Operations / abstraction
    def _get(self, path):
        """
            Wrapper of get() request to enforce some common parameters.
        """
        return self.get(path, json_ver=1)

    def _create(self, path, payload):
        """
            Wrapper of create request to enforce some common parameters.
        """
        return self.create(path, payload_json=payload, json_ver=1)

    # CDN abstraction
    def _cdn_origins_config(self, cdn_config):
        """
            Return CDN Origins configuration.

            :param str cdn_config: base CDN config to be get origins.
            :return: Return the Dict with CDN Origins configuration.
            :rtype : Dict
        """

        if isinstance(cdn_config, dict):
            path = '{:s}/{:d}/origins'.format(self.routes['cdn_config'],
                                              cdn_config['id'])
            cdn_config['origins'] = self._get(path)

        return cdn_config

    def _cdn_cache_config(self, cdn_config):
        """
            Return CDN Cache configuration.

            :param str cdn_config: base CDN config to be get cache settings.
            :return: Return the Dict with CDN Cache configuration.
            :rtype : Dict
        """

        if isinstance(cdn_config, dict):
            path = '{:s}/{:d}/cache_settings'.format(self.routes['cdn_config'],
                                                   cdn_config['id'])
            cdn_config['cache_settings'] = self._get(path)

        return cdn_config

    def _cdn_rules_config(self, cdn_config):
        """
            Return CDN Rules Engine configuration.

            :param str cdn_config: base CDN config to be get rules_engine.
            :return: Return the Dict with CDN Rules Engine configuration.
            :rtype : Dict
        """

        if isinstance(cdn_config, dict):
            path = '{:s}/{:d}/rules_engine'.format(self.routes['cdn_config'],
                                                   cdn_config['id'])
            cdn_config['rules_engine'] = self._get(path)

        return cdn_config

    def _cdn_config_expand(self, cdn_config):
        """
            Discovery and expand CDN configuration. This operation should be
            done because current API does not return all CDN config in base
            request.

            :param str cdn_config: CDN dict to be expaended.
            :return: Return the Dict with CDN configuration.
            :rtype : Dict

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
                c = self._get(path)
                if not isinstance(c, dict):
                    return cfg_all, 401

                if 'id' in c:
                    return (self._cdn_config_callback(c, option=option),
                            self.status['ok'])

                return cfg, status

            elif cdn_name is not None:
                cfg_all = self._get(self.routes['cdn_config'])
                if not isinstance(cfg_all, list):
                    return cfg_all, 401

                for c in cfg_all:
                    if c['name'] == cdn_name:
                        return (self._cdn_config_callback(c, option=option),
                                self.status['ok'])

                return cfg, status

            else:
                cfg = []
                cfg_all = self._get(self.routes['cdn_config'])
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

    def _cdn_check_payload(self, cdn_name, cdn_payload):
        """
            # TODO: Check CDN config payload is valid on creation.
        """
        return True

    def _create_cdn_recursive(self, cdn_payload):
        """
            Create the CDN recursively:
            1. CDN
            2. origins
            3. Cache Settings
            4. Rules Engine
        """

        ##> TODO: lookup certificate when CDN is using https, or just set ID
        path = '{:s}'.format(self.routes['cdn_config'])
        cdn_config = self._create(path, cdn_payload)

        if (not isinstance(cdn_config, dict)):
            return {'error': '{}'.format(cdn_config)}, self.status['not_found']

        # Origin
        try:
            cdn_payload['origins'] = sample.azion_cdn_origin(cdn_payload['name'])
        except Exception as e:
            return {'error': '{}'.format(cdn_config, e)}, self.status['exists']

        if ('origins' in cdn_payload):
            cdn_config['origins'] = []
            path = '{:s}/{:d}/origins'.format(self.routes['cdn_config'],
                                              cdn_config['id'])

            for o in cdn_payload['origins']:
                try:
                    cdn_config['origins'].append(self._create(path, o))
                except Exception as e:
                    return {'error': '{:s}'.format(e)}, self.status['not_found']

        # Cache
        cdn_payload['cache_settings'] = sample.azion_cdn_cache()
        if ('cache_settings' in cdn_payload):
            cdn_config['cache_settings'] = []
            path = '{:s}/{:d}/cache_settings'.format(self.routes['cdn_config'],
                                              cdn_config['id'])

            for o in cdn_payload['cache_settings']:
                # TODO: check if exists, change it?!
                try:
                    cdn_config['cache_settings'].append(self._create(path, o))
                except Exception as e:
                    return {'error': '{:s}'.format(e)}, self.status['not_found']

        # Rules
        cdn_payload['rules_engine'] = sample.azion_cdn_rules()
        if ('rules_engine' in cdn_payload):
            cdn_config['rules_engine'] = []
            re = cdn_config['rules_engine']
            path = '{:s}/{:d}/rules_engine'.format(self.routes['cdn_config'],
                                              cdn_config['id'])

            for r in cdn_payload['rules_engine']:
                # TODO: check if exists, change it?!
                try:
                    r['path_origin_id'] = lookup_id_from_name(r['path_origin_name'],
                                                              cdn_config['origins'])

                    if r['path_origin_id'] == 0:
                        re.append({"error": "{} Origin not found".format(r['path'])})
                        continue

                    r.pop('path_origin_name', None)
                except Exception as e:
                    re.append({"error": "create.rules_engine: {}".format(e)})
                    continue

                if 'cache_settings_name' in r:
                    try:
                        r['cache_settings_id'] = lookup_id_from_name(r['cache_settings_name'],
                                                                     cdn_config['cache_settings'])
                        if r['cache_settings_id'] == 0:
                            continue

                        r.pop('cache_settings_name', None)
                    except:
                        continue

                try:
                    cdn_config['rules_engine'].append(self._create(path, r))
                except Exception as e:
                    return {'error': '{:s}'.format(e)}, self.status['not_found']

        return (cdn_config, self.status['ok'])


    def _create_cdn(self, cdn_name, cdn_payload=None):
        """
            Create the CDN. Return it's configuration.
        """
        # If payload is not provided, generate from a sample
        if cdn_payload is None:
            cdn_payload = sample.azion_cdn(cdn_name)

        if isinstance(cdn_payload, dict):
            return self._create_cdn_recursive(cdn_payload)

        return {}, self.status['not_found']

    def create_cdn(self, cdn_name, cdn_payload=None):
        """
            Wrapper to create the CDN. Return it's configuration.

            :param str cdn_name: The operation to be done. Could be all, origin,
                cache and rules.
            :param dict cdn_payload: CDN ID to get the configuration.
            :return: Return the Dict with configuration recently created.
            :rtype : Dict
        """

        try:
            status = self.status['not_found']
            cfg = None
            if not self.api_has_session():
                self.init_api()

            cfg_all = self._get(self.routes['cdn_config'])
            if not isinstance(cfg_all, list):
                return cfg_all, 401

            for c in cfg_all:
                if c['name'] == cdn_name:
                    cfg = c

            if isinstance(cfg, dict):
                return cfg, self.status['exists']

            if not self._cdn_check_payload(cdn_name, cdn_payload):
                return {'error': 'Malformed payload'}, self.status['bad_request']

            return self._create_cdn(cdn_name, cdn_payload)

        except ServiceException as e:
            return {'{}'.format(e)}, self.status['server_error']
