# Man-in-the-Middle (MitM) Network Attack

This repository contains an example of a Man-in-the-Middle attack scenario, implemented as a CTF-style challenge.

## Task Description

There are three actors (containers) running in the same network:

- **Alice** - client
- **Bob** - server
- **Eve** - attacker

Bob is a standard HTTP server listening on port 80 and serving the contents of requested files.
Every 10 seconds, Alice sends a `GET` request to Bob asking for the contents of `public.html`.
The server also hosts another file: `secret.html`.

We play the role of Eve. Our task is to gain access to the contents of `secret.html` **without sending requests to Bob directly from Eve’s IP**.

The contents of `containers/bob/html/secret.html` must not appear in Alice’s container output.

##№ Assumptions

- The IP addresses of all participants are fixed for convenience and can be found in the `docker-compose` file.
- Assume the presence of a firewall that prevents Eve from making HTTP requests to Bob directly.
- Alice’s and Bob’s containers may not be modified.
- All actions must be carried out from Eve’s container.

## How to Run

Start the containers:

```bash
docker compose up --build
```

After launching the containers, `.pcap` files will appear in the `data` directory. 
These allow you to observe the network traffic in real time from Alice’s and Eve’s perspectives.

## Proposed Solution

An implementation of the attack can be found at: `containers/eve/content/attack.py`

The solution demonstrates:

1. **ARP spoofing** - to insert Eve between Alice and Bob.
2. **Sniffing** - capturing "typical traffic" between Alice and Bob (within the given constraints).
3. **TCP Injection** - modifying Alice’s request to Bob to point to a different file.
4. **TCP Injection** - altering Bob’s response to Alice with a previously captured one (the timestamp is updated to match Bob’s actual response, so Alice does not suspect tampering).
5. **ARP spoofing restoration** - reconnecting Alice and Bob directly after the successful attack ("covering tracks").
