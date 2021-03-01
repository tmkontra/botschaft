class MockRequests:
    class MockResponse:
        def __init__(self, status_code, *args, **kwargs):
            self.status_code = status_code
            self._args = args
            self._kwargs = kwargs

    def __init__(self):
        self.requests = []

    def get(self, *args, **kwargs):
        self.requests.append((args, kwargs))
        return self.MockResponse(200)
