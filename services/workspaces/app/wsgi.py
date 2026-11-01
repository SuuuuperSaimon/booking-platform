def application(request, start_response):
    if request["REQUEST_METHOD"] == "GET" and request["PATH_INFO"] == "/health":
        status = "200 OK"
        body = b'{"status":"ok"}'
    else:
        status = "404 Not Found"
        body = b'{"error":"not_found"}'

    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]

    start_response(status, headers)
    return [body]