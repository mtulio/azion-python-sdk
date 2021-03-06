# AZION Python SDK

[![PyPI](https://img.shields.io/pypi/v/azion.svg)](https://pypi.python.org/pypi/azion/)

Non-official [AZION](https://www.azion.com.br/) SDK written in Python.

## USE CASE

* [Ansible ROLE to manage CDN](https://github.com/mtulio/ansible-role-cloud-cdn)

## INSTALL

* From dev upstream

`pip install -e git+git@github.com:mtulio/azion-python-sdk.git@master#egg=azion`

* From PyPi

`pip install azion`

## DEPENDENCIES

* Valid user in [AZION platform]()
* An valid **session token** generated by your current credential. Eg.:
```shell
curl -s -X POST \
    -H "Accept: application/json; version=1" \
    -H "Authorization: Basic $(echo 'user@mail:mypass'|base64)" \
    https://api.azion.net/tokens
```
* Export session token in environment **AZION_TOKEN**. Eg.:
```shell
export AZION_TOKEN=<YOUR_SESSION_TOKEN>
```

## USAGE

* Create the session

> Will gets the AZION_TOKEN env

```python
from azion import AzionAPI
api = AzionAPI()
```

* Get all CDNs

```python
api.get_cdn_config()
```

* Get an CDN by NAME

```python
api.get_cdn_config(cdn_name='test-api')
```

* Get an CDN by ID

```python
api.get_cdn_config(cdn_id=14934121312)
```

* Get CDN's Origin config from an ID

```python
api.get_cdn_config(option='origin', cdn_id=14934121312)
```

* Get CDN's Cache config from an ID

```python
api.get_cdn_config(option='cache', cdn_id=14934121312)
```

* Get CDN's Rules Engine config from an ID

```python
api.get_cdn_config(option='rules', cdn_id=14934121312)
```

* Create a CDN's from the [Sample Config](./azion/sample.py)

```python
api.create_cdn(cdn_name='test-api')
```

> A tuple with dict of CDN config and ID will returned. See sample below

```python
In []: resp, status = api.cdn_config(cdn_name='test-api1')
In []: print status
In []: print json.dumps(resp, indent=4)
```


## TESTS

> TODOing

`python -m unittest`

## Get involved!

See [Contributing guide](CONTRIBUTING.md)

## CHANGELOG

### `0.2.0`

* Add support to CDN creation
* Add sample config to simplify from scratch

### `0.1.2`

* Add get CDN
* Improve description and docstrings

## TODO

* improve the logging and debbug
* [CDN] improve the validation before create.
 * check the existence of item, maybe change it?!
 * Payload sanity
* [CDN] add lookup Certificate on creation
* [CDN] add lookup Firewall before on creation/update Rules Engine
* [CDN] change the default ('/') Rule Engine to a custom origin
* improve docstrings and it's builder
* improve return codes. Eg. based on what API returned
* improve the time to creation the CDN.
* Add unit tests
