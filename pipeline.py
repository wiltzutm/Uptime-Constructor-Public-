
import csv
import datetime
import warnings
import pathlib
import functools


import pandas as pd

# This is just a personal test to mark missing values with an object. Isn't neccessary.
MISSING = object()


def iter_csv_rows(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        # Skip the first row:
        _ = next(reader)
        for line in reader:
            yield line


def map_csv_fields(row_iter):
    for row in row_iter:
        # There's no point in initializing new_row like this because if the value
        # really is missing from the row, then the python will raise exception and
        # as you see we don't handle our exceptions at all here. Same applies to other
        # pipeline functions...
        new_row = {'epoch_us': MISSING, 'acceleration_si': MISSING}
        new_row['epoch_us'] = float(row[0])
        new_row['acceleration_si'] = float(row[1])
        yield new_row


def convert_epoch_to_timestamp(row_batch_iter):
    for row in row_batch_iter:
        new_row = {**row}
        _ = new_row.pop("epoch_us")
        new_row['datetime'] = MISSING
        new_row['datetime'] = datetime.datetime.utcfromtimestamp(
            row['epoch_us'])
        yield new_row


def split_datetimes(row_batch_iter):
    for row in row_batch_iter:
        new_row = {**row}
        _ = new_row.pop('datetime')
        new_row['date'] = MISSING
        new_row['time'] = MISSING
        new_row['date'] = row['datetime'].date()
        new_row['time'] = row['datetime'].time()
        yield new_row


def convert_acceleration_si_to_g(row_batch_iterator):
    for row in row_batch_iterator:
        new_row = {**row}
        _ = new_row.pop("acceleration_si")
        new_row["acceleration_g"] = MISSING
        new_row['acceleration_g'] = row['acceleration_si'] / 9.81
        yield new_row


# You could do most of the steps in a single generator function.
# That would probably save some memory and processing power.
pipeline_for_single_file = [
    iter_csv_rows,
    map_csv_fields,
    convert_epoch_to_timestamp,
    split_datetimes,
    convert_acceleration_si_to_g
]


def run_pipeline(pipeline, filepath):
    return functools.reduce(lambda f, g: g(f), pipeline, filepath)


def run_pipeline_for_single_csv(filepath):
    return run_pipeline(pipeline_for_single_file, filepath)


columns = []
datafilepaths = [("sensor 1", "./test_data/data-sensor1.csv"), ("sensor2", "./test_data/data-sensor2.csv"), ("sensor3", "./test_data/data-sensor3.csv")]
for name, filepath in datafilepaths:
    column = pd.DataFrame.from_records(
        list(run_pipeline_for_single_csv(filepath)), index=["date", "time"])
    column.rename({'acceleration_g': name}, axis=1, inplace=True)
    columns.append(column)
result = pd.concat(columns) # This could be changed to non copying with copy=False
result.sort_index(inplace=True)
print(result.head(20))
print(result.tail(20))
# Now what should we do with the nans? fillna with maybe mean padding?
