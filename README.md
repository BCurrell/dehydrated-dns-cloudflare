# dehydrated-dns-cloudflare

Dehydrated hook for DNS verification on Cloudflare in Python.

Whilst there are already 2 recommended dehydrated hooks for DNS verification with Cloudflare, I still had reasons for creating this project.

1) The one written in Python doesn't use the Cloudflare library, and requires you to install requirements globally.
2) I wanted to get an understanding of dehydrated hooks before creating one for Hurricane Electric.

You're welcome to use one of the existing (recommended) hooks, or you're welcome to use mine. Any feedback, bug reports, suggestions and/or pull requests are also welcome.

## Requirements

- dehydrated
- python (3.6 or higher)
- poetry

For the purposes of this "documentation", I'm assuming you already have these installed, or know how to install them.

## Usage

The following instructions assume the following:

- You store your dehydrated hooks in `/etc/dehydrated/hooks/`

You can store dehydrated hooks wherever you want, just update the paths when you run the commands.

- You are using dehydrated with CLI args, not the config file

If you prefer to use config files, read the dehydrated documentation and adjust accordingly.

```shell
cd /etc/dehydrated/hooks/
git clone https://github.com/BCurrell/dehydrated-dns-cloudflare.git dns-cloudflare
cd dns-cloudflare
poetry install
cp .env.sample .env
nano .env
```

```shell
dehydrated -c -d testing.example.com -t dns-01 -k /etc/dehydrated/hooks/dns-cloudflare/hook.sh
```

## To-Do

- [x] Initial commit with basic functionality.
- [ ] Better logging. Or just some logging at all.
- [ ] Better error handling.
