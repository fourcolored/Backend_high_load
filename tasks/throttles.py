from rest_framework.throttling import UserRateThrottle

class AdminThrottle(UserRateThrottle):
    rate = '10000/hour'

class RegularUserThrottle(UserRateThrottle):
    rate = '1000/hour'