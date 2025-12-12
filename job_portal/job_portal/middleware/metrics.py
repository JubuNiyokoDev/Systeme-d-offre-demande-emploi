import time
from prometheus_client import Histogram, Counter

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "Latency of HTTP requests", ["method", "endpoint"]
)
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)


class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        latency = time.time() - start_time

        # Collect metrics
        REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

        return response
