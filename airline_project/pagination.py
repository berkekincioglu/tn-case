"""
Custom pagination classes for the Airline Management System API.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that allows clients to control page size.

    Query Parameters:
    - page: Page number (default: 1)
    - limit: Number of items per page (default: 10, max: 100)

    Response Format:
    - count: Total number of items
    - next: Next page number (or null)
    - previous: Previous page number (or null)
    - results: Array of items

    Example:
    - /api/flights/?page=1&limit=10
    - /api/airplanes/?page=2&limit=5
    """
    page_size = 10  # Default page size
    page_size_query_param = 'limit'  # Allow client to set page size via 'limit' parameter
    max_page_size = 100  # Maximum allowed page size
    page_query_param = 'page'  # Page number parameter

    def get_paginated_response(self, data):
        """
        Return paginated response with page numbers instead of URLs.
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.page.previous_page_number() if self.page.has_previous() else None,
            'results': data
        })
