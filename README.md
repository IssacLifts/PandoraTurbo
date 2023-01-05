# Pandora Turbo
A Turbo sniper using sockets and threading

This turbo will likely be entirely inefficent unless you have 50+ accounts

## ! IMPORT
If you don't have python 3.11 this won't work

## Config guide
* nc if for microsoft accounts
* gc is for giftcode accounts
* ncgc is for giftcode and microsoft account sniping
* ncb is for bearers and microsoft accounts
* gcb is for giftcode and bearer accounts

  Enter your accounts in the 'accounts' list in "EMAIL:PASSWORD", format.

    Example config file:
    ```{
        "account_type": "nc",
        "bearers": [],
        "accounts": ["ACCOUNT1@gmail.com:acc",
                    "ACCOUNT2@gmail.com:acc"],
        "skin_change": true,
        "skin_variant": "slim",
        "skin_url": "https://s.namemc.com/i/d1a1e9827d20cd36.png",
        "proxies": [{"host": "127.0.0.1", "port": 80, "proxy_type": "SOCK5"},
                    {"host": "127.0.0.1", "port": 81, "proxy_type": "SOCK4"},
                    {"host": "127.0.0.1", "port": 82, "proxy_type": "HTTP"}]
        }
    ```

    Leave 'proxies' as [] if you're not using proxies.

## Modules used
* colorama
* msmcauth
* requests
* sockets
* ssl

## Utilizes sockets and SSL
```python
    sock.connect(('api.minecraftservices.com', 443))
    sock_ = ssl.create_default_context().wrap_socket(sock, server_hostname='api.minecraftservices.com')
    sock_.send(self.check_payload)
    data = sock_.recv(1024).decode('utf-8')
```

## Status codes
* 429 = Rate Limited
* 200 = Success
* 403 = Forbidden

