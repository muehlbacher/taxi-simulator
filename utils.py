import numpy as np
from dataclasses import dataclass
import queue
from datetime import datetime


def taxi_id_number(num_taxis):
    arr = np.arange(num_taxis)
    np.random.shuffle(arr)
    for i in range(num_taxis):
        yield arr[i]

def shift_info():
    start_times_and_freqs = [(0,8),(8,30),(16,15)]
    indices = np.arange(len(start_times_and_freqs))
    while True:
        idx = np.random.choice(indices, p = [0.25,0.5,0.25])
        start = start_times_and_freqs[idx]
        yield (start[0], start[0] + 7.5, start[1])

def taxi_process(taxi_id_generator, shift_info_generator):
    taxi_id = next(taxi_id_generator)
    shift_start, shift_end, shift_mean_trips = next(shift_info_generator)
    actual_trips = round(np.random.normal(loc = shift_mean_trips, scale = 2))

    average_trip_time = 6.5 / shift_mean_trips * 60
    between_event_time = 1.0 / (shift_mean_trips -1 ) * 60

    time = shift_start

    yield TimePoint(taxi_id, 'start shift', format_time(time))
    
    deltaT = np.random.poisson(between_event_time) / 60

    time += deltaT
    
    for _ in range(actual_trips):
        yield TimePoint(taxi_id, 'pick up   ', format_time(time))
        deltaT = np.random.poisson(average_trip_time) / 60
        time += deltaT
        yield TimePoint(taxi_id, 'drop off  ', format_time(time))
        deltaT = np.random.poisson(between_event_time) / 60
        time += deltaT
    deltaT = np.random.poisson(between_event_time) / 60
    time += deltaT
    yield TimePoint(taxi_id, 'end shift ', format_time(time))


@dataclass
class TimePoint:
    taxi_id: int
    name: str
    time: datetime
    
    def __lt__(self, other):
        #print(f"self:{self.time}")
        #print(f"other:{other.time}")
        return self.time < other.time

class Simulator:
    def __init__(self, num_taxis):
        self._time_points = queue.PriorityQueue()
        taxi_id_generator = taxi_id_number(num_taxis)
        shift_info_generator = shift_info()
        self._taxis = [taxi_process(taxi_id_generator, shift_info_generator) for _ in range(num_taxis)]
        self._prepare_run()
    
    def _prepare_run(self):
        for t in self._taxis:
            while True:
                try:
                    e = next(t)
                    self._time_points.put(e)
                except:
                    break
    def run(self):
        sim_time = "00:00"
        while sim_time < "24:00":
            if self._time_points.empty():
                break
            p = self._time_points.get()
            sim_time = p.time
            print(p)

def format_time(time):
    hour = int(time)
    minute = int(60 * (time - (int(time))))
    time_formatted = datetime.strptime(f"{hour}:{minute}", "%H:%M").strftime("%H:%M")
    return time_formatted