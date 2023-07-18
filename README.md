# Project Name
Asynchronous Proxy Server using caching

## Overview
The Asynchronous Proxy Server is a Python application that forwards clients' REST requests to a remote server while enforcing rate limits. It utilizes asynchronous programming and caching to optimize performance and reduce requests to the remote server. The server responds asynchronously to clients, providing efficient handling of simultaneous requests.

## Constant Variables

| Constant                  | Description                           |
|---------------------------|---------------------------------------|
| REQUESTS_PER_MINUTE_LIMIT | Maximum number of requests per minute |
| REQUESTS_PER_DAY_LIMIT    | Maximum number of requests per day    |
| CACHE_DURATION_MINUTES    | Duration of cache validity in minutes |

## How to use the server

- Run "pip install -r requirements.txt" in the Terminal
- Run "python .\proxy_server.py" in the Terminal
- Open a postman ot the browser and try yo make a get request to the server
  for example with this url: http://localhost:8080/listusers?page=2
