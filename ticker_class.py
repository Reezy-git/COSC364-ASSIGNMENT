"""
 timer.py: Periodic Timer Event.

 COSC364 RIP2 Assignment

 Author:
 - Richard Hodges (11139316)
 - Chrystel Claire Quirimit (63369627)

"""


import threading


class Ticker:
    """Ticks every duration"""
    def __init__(self, owner, duration=30):
        self.thread = None
        self.duration = duration
        self.owner = owner

    def loop(self):
        self.owner.on_tick()  # the true action
        self.thread = threading.Timer(self.duration, self.loop)  # sets a timer with function to call self.on_tick
        self.thread.start()  # starts that timer
