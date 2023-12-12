import json

TWO_TIMER_QUEUE = [
                {
                    "name": "김동수"
                },
                {
                    "name": "김태언"
                },
                {
                    "name": "황지훈"
                },
                {
                    "name": "채현우"
                },
                {
                    "name": "최진영"
                }
]

def two_timers(avail_workers):
    # Get two timers based on the number of available workers
    # Weekdays If we got 9 people, we need 1 more to serve 2 times
    # then loop once \
    # if we need 2 more to serve, find 2 more]
    return 