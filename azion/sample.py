

def azion_cdn(cdn_name):
    """
        Create default CDN attributes.
    """
    return {
        "name": cdn_name,
        "origin_address": "domain.{}".format(cdn_name),
        "cname_access_only": True,
        "cname": ["www1.{}".format(cdn_name)],
        "delivery_protocol": "http",
        "cdn_cache_settings": "override",
        "cdn_cache_settings_minimum_ttl": 2592000,
        "origin_protocol_policy": "preserve"
    }

def azion_cdn_origin(cdn_name):
    """
        Create default CDN Rules Engine config.
    """
    return [
            {
                "name": "origin-default",
                "origin_type": "single_origin",
                "host_header": "www.{}".format(cdn_name),
                "origin_protocol_policy": "https",
                "addresses": [
                    {
                     "address": "origin-www.{}".format(cdn_name)
                    }
                ],
                "connection_timeout": 10,
                "timeout_between_bytes": 30
            },
            {
                "name": "origin-balanced",
                "origin_type": "load_balancer",
                "method": "ip_hash",
                "host_header": "www-lb.{}".format(cdn_name),
                "origin_protocol_policy": "preserve",
                "addresses": [
                    {
                     "address": "www-lb1.{}".format(cdn_name),
                     "weight": 10,
                     "server_role": "primary",
                     "is_active": True
                    },
                    {
                     "address": "origin-lb2.{}".format(cdn_name),
                     "weight": 1,
                     "server_role": "backup",
                     "is_active": True
                    }
                ],
                "connection_timeout": 10,
                "timeout_between_bytes": 30
            },
            {
                "name": "origin-static",
                "origin_type": "single_origin",
                "host_header": "static.{}".format(cdn_name),
                "origin_protocol_policy": "http",
                "addresses": [
                    {
                     "address": "origin-static.{}".format(cdn_name)
                    }
                ],
                "connection_timeout": 10,
                "timeout_between_bytes": 20
            },
            {
                "name": "origin-proxy",
                "origin_type": "single_origin",
                "host_header": "proxy.{}".format(cdn_name),
                "origin_protocol_policy": "preserve",
                "addresses": [
                    {
                     "address": "origin-proxy.{}".format(cdn_name)
                    }
                ],
                "connection_timeout": 10,
                "timeout_between_bytes": 20
            }
        ]


def azion_cdn_cache():
    """
        Create default CDN Cache settings.
    """
    return  [
      {
        "name": "cache-1-hour-ignore-qs-cookies",
        "browser_cache_settings": False,
        "cdn_cache_settings": "override",
        "cdn_cache_settings_maximum_ttl": 3600,
        "cache_by_query_string": "ignore",
        "enable_query_string_sort": False,
        "cache_by_cookies": "ignore",
      },
      {
        "name": "cache-5-minutes-ignore-qs-cookies",
        "browser_cache_settings": False,
        "cdn_cache_settings": "override",
        "cdn_cache_settings_maximum_ttl": 300,
        "cache_by_query_string": "ignore",
        "enable_query_string_sort": False,
        "cache_by_cookies": "ignore",
      },
      {
        "name": "cache-bypass",
        "browser_cache_settings": False,
        "cdn_cache_settings": "bypass",
        "cache_by_query_string": "ignore",
        "cache_by_cookies": "ignore",
      }
    ]


def azion_cdn_rules():
    """
        Create default CDN Rules Engine config.
    """
    return [
          {
            "path": "/images/",
            "regex": False,
            "protocol_policy": "http,https",
            "gzip": True,
            "behavior": "delivery",
            "path_origin_name": "origin-static",
            "cache_settings_name": "cache-1-hour-ignore-qs-cookies"
          },
          {
            "path": "/fonts/",
            "regex": False,
            "protocol_policy": "http,https",
            "gzip": True,
            "behavior": "delivery",
            "path_origin_name": "origin-static",
            "cache_settings_name": "cache-1-hour-ignore-qs-cookies"
          },
          {
            "path": "/css/",
            "regex": False,
            "protocol_policy": "http,https",
            "gzip": True,
            "behavior": "delivery",
            "path_origin_name": "origin-static",
            "cache_settings_name": "cache-5-minutes-ignore-qs-cookies"
          },
          {
            "path": "/js/",
            "regex": False,
            "protocol_policy": "http,https",
            "gzip": True,
            "behavior": "delivery",
            "path_origin_name": "origin-static",
            "cache_settings_name": "cache-5-minutes-ignore-qs-cookies"
          },
          {
            "path": "/proxy",
            "regex": False,
            "protocol_policy": "http",
            "gzip": True,
            "behavior": "acceleration",
            "path_origin_name": "origin-proxy",
            "cache_settings_name": "cache-bypass",
            "forward_cookies": "all"
          },
          {
            "path": "/site",
            "regex": False,
            "protocol_policy": "http",
            "gzip": True,
            "behavior": "acceleration",
            "path_origin_name": "origin-default",
            "cache_settings_name": "cache-bypass",
            "forward_cookies": "all"
          }
    ]
