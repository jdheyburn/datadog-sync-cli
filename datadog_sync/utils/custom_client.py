import time

import requests


def request_with_retry(func):
    def wrapper(*args, **kwargs):
        retry = True
        timeout = time.time() + 60 * 5
        default_backoff = 5
        retry_count = 0
        resp = None

        while retry and timeout > time.time():
            try:
                resp = func(*args, **kwargs)
                resp.raise_for_status()
                retry = False
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 429 and "x-ratelimit-reset" in e.response.headers:
                    try:
                        backoff = int(e.response.headers["x-ratelimit-reset"])
                    except ValueError:
                        backoff = retry_count * default_backoff
                    time.sleep(backoff)
                    retry_count += 1
                    continue
                elif status_code >= 500:
                    time.sleep(retry_count * default_backoff)
                    retry_count += 1
                    continue
                raise e
        return resp

    return wrapper


class CustomClient:
    def __init__(self, host, auth):
        self.host = host
        self.timeout = 30
        self.session = requests.Session()
        self.session.headers.update(build_default_headers(auth))

    @request_with_retry
    def get(self, path, **kwargs):
        url = self.host + path
        return self.session.get(url, timeout=self.timeout, **kwargs)

    @request_with_retry
    def post(self, path, body, **kwargs):
        url = self.host + path
        return self.session.post(url, json=body, timeout=self.timeout, **kwargs)

    @request_with_retry
    def put(self, path, body, **kwargs):
        url = self.host + path
        return self.session.put(url, json=body, timeout=self.timeout, **kwargs)

    @request_with_retry
    def patch(self, path, body, **kwargs):
        url = self.host + path
        return self.session.patch(url, json=body, timeout=self.timeout, **kwargs)

    def delete(self, path, body, **kwargs):
        url = self.host + path
        return self.session.delete(url, json=body, timeout=self.timeout, **kwargs)


def build_default_headers(auth_obj):
    headers = {
        "DD-API-KEY": auth_obj["apiKeyAuth"],
        "DD-APPLICATION-KEY": auth_obj["appKeyAuth"],
        "Content-Type": "application/json",
    }
    return headers


def paginated_request(func):
    def wrapper(*args, **kwargs):
        page_size = 100
        page_number = 0
        remaining = 1
        resources = []
        while remaining > 0:
            params = {"page[size]": page_size, "page[number]": page_number}
            kwargs.update({"params": params})

            resp = func(*args, **kwargs)
            resp.raise_for_status()

            resp_json = resp.json()
            resources.extend(resp_json["data"])
            remaining = int(resp_json["meta"]["page"]["total_count"]) - (page_size * (page_number + 1))
            page_number += 1
        return resources

    return wrapper
