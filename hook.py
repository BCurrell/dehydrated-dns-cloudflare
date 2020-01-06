#!/usr/bin/env python3

"""
"""

from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError
from dns.resolver import Resolver, NXDOMAIN
from dns.exception import DNSException
from dotenv import load_dotenv
from sys import argv
from time import sleep
from tld import parse_tld

load_dotenv()


prefix = "_acme-challenge."
cloudflare = CloudFlare()


def get_zone_id(domain):
    tld, domain, subdomain = parse_tld(domain, fix_protocol=True)

    if domain is None:
        # TODO: Fail with grace
        exit(1)

    fld = ".".join((domain, tld))

    try:
        zone = cloudflare.zones.get(params={'name': fld})[0]
    except CloudFlareAPIError as e:
        # TODO: Fail with grace
        print(e)
        exit(1)

    return zone["id"], fld, subdomain


def dns_lookup(name, resolver=None):
    if resolver is None:
        resolver = Resolver()

    try:
        yield from [str(record) for record in resolver.query(name, "TXT")]
    except NXDOMAIN:
        yield None
    except DNSException as e:
        # TODO: Fail with grace
        print(e)
        exit(1)


def dns_verify(name, content):
    retries = 3
    resolver = Resolver()

    if content is not None:
        content = f"\"{content}\""

    for retry in range(retries):
        sleep(10)

        result = dns_lookup(name, resolver)

        if content in result:
            return True

    return False


def add_record(zone, name, content):
    record = {
        "name": name,
        "content": content,
        "type": "TXT",
        "ttl": 120,
        "proxied": False,
    }

    try:
        result = cloudflare.zones.dns_records.post(zone, data=record)
    except CloudFlareAPIError as e:
        # TODO: Fail with grace
        print(e)
        exit(1)


def remove_record(zone, name, content):
    params = {
        "name": name,
        "content": content,
    }

    dns_records = cloudflare.zones.dns_records.get(zone, params=params)

    try:
        for record in dns_records:
            result = cloudflare.zones.dns_records.delete(zone, record["id"])
    except CloudFlareAPIError as e:
        # TODO: Fail with grace
        print(e)
        exit(1)


def deploy_challenge(*args):
    name = prefix + args[0]
    content = args[2]

    zone, fld, subdomain = get_zone_id(name)

    add_record(zone, name, content)

    dns_verify(name, content)


def clean_challenge(*args):
    name = prefix + args[0]
    content = args[2]

    zone, fld, subdomain = get_zone_id(name)

    remove_record(zone, name, content)

    dns_verify(name, None)


def main():
    try:
        operation, args = argv[1], argv[2:]
    except IndexError:
        # TODO: Fail with grace
        print("Invalid argv!")
        exit(1)

    operations = {
        "deploy_challenge": deploy_challenge,
        "clean_challenge": clean_challenge,
    }

    if operation in operations:
        operations[operation](*args)        


if __name__ == "__main__":
    main()
