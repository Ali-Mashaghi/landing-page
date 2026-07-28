from rest_framework.throttling import AnonRateThrottle


class ContactSubmissionThrottle(AnonRateThrottle):
    rate = '5/min'

    def allow_request(self, request, view):
        if request.method != 'POST':
            return True
        return super().allow_request(request, view)
