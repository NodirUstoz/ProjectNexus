"""
Custom pagination classes for the ProjectNexus API.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination used across all list endpoints."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data["total_pages"] = self.page.paginator.num_pages
        response.data["current_page"] = self.page.number
        response.data["page_size"] = self.get_page_size(self.request)
        return response


class SmallResultsSetPagination(PageNumberPagination):
    """Smaller page size for lightweight lists like comments or activity."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class LargeResultsSetPagination(PageNumberPagination):
    """Larger page size for export-like endpoints."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500
