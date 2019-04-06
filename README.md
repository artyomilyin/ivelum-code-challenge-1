# ivelum-code-challenge-1

This is a simple http-proxy-server, that displays pages from habrahabr.ru, 
but modifies any 6-letter word adding `™` character to it.

Any link on the page which leads to another habrahabr.ru page 
is also modified to point to this proxy-server's address.

The server uses `requests` and `beautifulsoup4` packages.

### Usage:
`python3 ./server.py` to run it on default `8080` port
#### or
`python3 ./server.py 12345` to run it on port `12345` or any other available port.


### Tests:
`python3 ./tests.py` if the server runs on default `8080` port
#### or
`python3 ./tests.py 12345` if the server runs on port `12345` or any other port.