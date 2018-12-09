#!/usr/bin/env python
import sys
import datetime
import re

PST_TO_EST = datetime.timedelta(hours=3)
ZIP_CHARS = 5
DUR_PATTERN = re.compile(r'(\d+):(\d+):(\d+)\.(\d+)')


def csv_transform():
    # Open the stdin and create a list of lines
    f = open(sys.argv[1])
    data = f.read().splitlines()

    # Read the headers at index 0
    headers = data[0].split(',')

    # Read each line and process it
    for line in data[1:]:
        row = line.split(',')
        # Catch errors associated with data.
        # Expected errors from invalid data are from strptime(ValueError) and re match(AttributeError)
        try:
            trans_row = transform_row(headers, row)
        except (ValueError, AttributeError), e:
            sys.stderr.write('Invalid data. Skipping row. %s\n' % e)
            continue

        # Print each entry to stdout and a comma if this is not the last entry of the line
        for i in range(len(headers)):
            sys.stdout.write(trans_row[i])
            if i != len(headers) - 1:
                sys.stdout.write(',')
        # Next line print to stdout
        sys.stdout.write('\n')


def transform_row(headers, row):
    foo_duration = 0
    bar_duration = 0
    # Process according to header order
    for i in range(len(headers)):
        if headers[i] == 'Timestamp':
            # Convert to datetime
            date = datetime.datetime.strptime(row[i], '%m/%d/%y %I:%M:%S %p') + PST_TO_EST
            # Replace the Timestamp with the date in ISO-8601
            row[i] = date.isoformat()
        elif headers[i] == 'Address' or headers[i] == 'Notes':
            # We will need to fix the comma based split done above if there is '"'
            if '"' in row[i]:
                while row[i].count('"') == 1:
                    nxt = row.pop(i + 1)
                    row[i] = row[i] + ',' + nxt
        elif headers[i] == 'ZIP':
            # Fill in zeroes for ZIP
            row[i] = row[i].zfill(ZIP_CHARS)
        elif headers[i] == 'FullName':
            # Set name to upper case
            row[i] = row[i].upper()
        elif headers[i] == 'FooDuration' or headers[i] == 'BarDuration':
            # Match according to our duration pattern
            match = DUR_PATTERN.search(row[i])
            # Create a timedelta object and output the seconds in float
            dur = datetime.timedelta(hours=int(match.group(1)), minutes=int(match.group(2)),
                                     seconds=int(match.group(3)), milliseconds=int(match.group(4)))
            row[i] = str(dur.total_seconds())
            # Save the durations so they can be added later
            if headers[i] == 'FooDuration':
                foo_duration = dur.total_seconds()
            else:
                bar_duration = dur.total_seconds()
        elif headers[i] == 'TotalDuration':
            # Add the durations. This only works if the TotalDuration column comes after
            # Foo and Bar
            row[i] = str(foo_duration + bar_duration)

    return row


if __name__ == '__main__':
    csv_transform()
