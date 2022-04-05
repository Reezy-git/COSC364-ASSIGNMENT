from threading import Timer
import time

class Owner:
    def __init__(self):
        return
    def on_tick(self):
        print('tick')

# class Tick_Timer(Timer):
#     def __init__(self, owner, duration=30):
#         self.owner = owner
#         self.tick_duration = duration
#
#     def run(self):
#         while True:
#             time.sleep(self.tick_duration)
#             self.owner.on_tick()


a = Owner()


def tick(owner, timer):
    owner.on_tick()
    timer.start()


tick_timer = Timer(3, tick, [a, tick_timer])

print('meanwhile')
time.sleep(2)
print('we do stuff')
time.sleep(5)
tick_timer.cancel()
