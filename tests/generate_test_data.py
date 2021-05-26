""" This is just a simple script to create some proper test data.
"""

import datetime
import random
import math
import csv
import pathlib


def generate_acceleration(start: datetime.datetime, duration: int, sample_rate: int, amp: float, freq: float):
    data = []
    dt = 1.0/sample_rate
    for i in range(1, duration*sample_rate+1):
        time = dt*float(i)
        ts = start + datetime.timedelta(microseconds=time*1e6)
        ts_epoch = ts.timestamp()
        acc = amp*math.sin(freq*time)
        data.append((ts_epoch, acc))
    return data


# Samples per second:
sample_rate = 6000
# Sampling duration in seconds:
duration = 15
gathering_start = datetime.datetime.strptime(
    "2020-05-26 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f')
headers = ["Time stamp", "Value"]
sensors = ["sensor1", "sensor2", "sensor3"]
amps = [15.0, 5.0, 2.0]
freqs = [math.pi*2.0/3.0, math.pi*3.0, math.pi*2.0]

# Generate some data and randomize the selection process by selection 2/3 of the full
# sample.
datas = {}
for name, amp, freq in zip(sensors, amps, freqs):
    gen_data = generate_acceleration(
        gathering_start, duration, sample_rate, amp, freq)
    datas[name] = random.sample(gen_data, k=2*(duration*sample_rate) // 3)
    datas[name].sort()

# Create the test_data folder if it doesn't exist. Well maybe the if is redundant, one
# could create it anyways.
folder = pathlib.Path("./test_data")
if not folder.exists():
    folder.mkdir()
# Write all datas into files:
for name, values in datas.items():
    with open(folder/f"data-{name}.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(values)
