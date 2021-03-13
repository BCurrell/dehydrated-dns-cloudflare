#!/usr/bin/env python3

"""
"""
import click
from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError
from dns.resolver import Resolver, NXDOMAIN
from dns.exception import DNSException
from dotenv import load_dotenv
from time import sleep
from tld import parse_tld

load_dotenv()


prefix = "_acme-challenge."
cloudflare = CloudFlare()


def _get_zone_id(domain):
    tld, domain, subdomain = parse_tld(domain, fix_protocol=True)

    if domain is None:
        # TODO: Fail with grace
        exit(1)

    fld = ".".join((domain, tld))

    try:
        zone = cloudflare.zones.get(params={"name": fld})[0]
    except CloudFlareAPIError as e:
        # TODO: Fail with grace
        click.echo(e, err=True)
        exit(1)

    return zone["id"], fld, subdomain


def _dns_lookup(name, resolver=None):
    if resolver is None:
        resolver = Resolver()

    try:
        yield from [str(record) for record in resolver.query(name, "TXT")]
    except NXDOMAIN:
        yield None
    except DNSException as e:
        # TODO: Fail with grace
        click.echo(e, err=True)
        exit(1)


def _dns_verify(name, content):
    retries = 3
    resolver = Resolver()

    if content is not None:
        content = f'"{content}"'

    for retry in range(retries):
        sleep(10)

        result = _dns_lookup(name, resolver)

        if content in result:
            return True

    return False


def _add_record(zone, name, content):
    record = {
        "name": name,
        "content": content,
        "type": "TXT",
        "ttl": 120,
        "proxied": False,
    }

    try:
        _ = cloudflare.zones.dns_records.post(zone, data=record)
    except CloudFlareAPIError as e:
        # TODO: Fail with grace
        click.echo(e, err=True)
        exit(1)


def _remove_record(zone, name, content):
    params = {
        "name": name,
        "content": content,
    }

    dns_records = cloudflare.zones.dns_records.get(zone, params=params)

    try:
        for record in dns_records:
            _ = cloudflare.zones.dns_records.delete(zone, record["id"])
    except CloudFlareAPIError as e:
        # TODO: Fail with grace
        click.echo(e, err=True)
        exit(1)


def _normalize_click_args(name):
    # This allows Click to accept arguments with underscores like the ones dehydrated uses.
    # Simply replaces underscores from input to hyphens before they go through Click's parser.
    # With this, arguments can be passed as foo-bar or foo_bar.
    return name.replace("_", "-")


@click.group(context_settings={"token_normalize_func": _normalize_click_args})
def cli_main():
    pass


@cli_main.command()
@click.argument("domain")
@click.argument("token-file")
@click.argument("token")
def deploy_challenge(domain, token_file=None, token=None):
    domain = prefix + domain
    zone, fld, subdomain = _get_zone_id(domain)

    _add_record(zone, domain, token)
    _dns_verify(domain, token)


@cli_main.command()
@click.argument("domain")
@click.argument("token-file")
@click.argument("token")
def clean_challenge(domain, token_file=None, token=None):
    domain = prefix + domain
    zone, fld, subdomain = _get_zone_id(domain)

    _remove_record(zone, domain, token)
    _dns_verify(domain, None)


if __name__ == "__main__":
    cli_main()
