# azuremetadata

## Running in development

#### Running the stub metadata server locally

1. Run `./stub_server.py` -- it serves fixtures from `fixtures` directory on port 8888.
2. Redirect packets for `169.254.169.254:80` to `127.0.01:8888`:
```bash
iptables -t nat -A OUTPUT -p tcp -d 169.254.169.254 -j DNAT --to-destination 127.0.0.1:8888
```

#### Running the command-line tool

```bash
export PYTHONPATH=./lib ./azuremetadata
```

#### Running tests

```bash
make test
make coverage
```
