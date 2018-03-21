"""
Extracts top player scores from files written in NBT format.
Written by Prof_Bloodstone (aka B1o0dy) for use at Near Vanilla server.
"""
from __future__ import division

import argparse
import shutil
import tempfile
import os
import json
import time
import sys
from contextlib import contextmanager
from collections import namedtuple, defaultdict
from math import log

from nbt import nbt

if sys.version_info < (3, 5):
    try:
        from scandir import scandir
    except ImportError:
        DirEntry = namedtuple('DirEntry', ('path', 'is_file'))

        def scandir(directory):
            paths = (os.path.join(directory, filename) for filename in os.listdir(directory))
            return (DirEntry(path, lambda: os.path.isfile(path)) for path in paths)
else:
    from os import scandir

PLAYER_SCORE = namedtuple('PLAYER_SCORE', ['name', 'score'])


def ticks_to_time(ticks):
    sec = ticks // 20
    minutes = (sec // 60) % 60
    hours = sec // 3600
    return '{} hours {} minute{}'.format(hours, minutes, 's' if minutes != 1 else '')


def extract_scores(nbtfile):
    """Extract scores from nbt file and convert to python format that is easier to work with."""
    objectives = {str(tag['Name']): {}
                  for tag in nbtfile['data']['Objectives'].tags}
    player_scores = nbtfile['data']['PlayerScores']

    for score in player_scores:
        player_name = str(score['Name'])
        objective = str(score['Objective'])
        objectives[objective][player_name] = int(str(score['Score']))

    return objectives


def parse_scores(nbtfile, number):
    objectives = extract_scores(nbtfile)

    scoreboard = {}
    blocks_traveled = defaultdict(int)

    for key, obj in objectives.items():
        if key.startswith('Time'):
            l = sorted([
                PLAYER_SCORE(name, score)
                for name, score
                in obj.items()
            ],
                key=lambda x: x.score,
                reverse=True)
            # not used anymore and contains a bug. fix it before uncommenting
            # # # # # scoreboard['total_playtime'] = (('{} hours'.format(sum(x.score for x in l) // (20 * 60 * 60)),),)
            l = [PLAYER_SCORE(name, ticks_to_time(score))
                 for name, score in l]

        elif key.startswith('Distance_'):
            for name, score in obj.items():
                blocks_traveled[name] += score
            continue

        else:
            l = sorted([
                PLAYER_SCORE(name, score)
                for name, score
                in obj.items()
            ],
                key=lambda x: x.score,
                reverse=True)

        scoreboard[key] = [{'playerName': name, 'score': score}
                           for name, score
                           in l[: None if number <= 0 else number]]

    # convert `blocks_traveled from dict to sorted list
    blocks_traveled = sorted([PLAYER_SCORE(name, score)
                              for name, score in blocks_traveled.items()],
                             key=lambda x: x.score,
                             reverse=True)
    # format it so it has G blocks, M blocks and K blocks
    prefixes = ['', 'K', 'M', 'G', 'T', 'times Nathan cheated']
    blocks_traveled = [{
        'playerName': name,
        'score': '{:5.1f}{:1} blocks'.format(
            score / 10 ** (2 + 3 * int(log(score / 100, 1000))),
            prefixes[int(log(score / 100, 1000))]
        )
    }
        for name, score in blocks_traveled]
    scoreboard['blocks_traveled'] = blocks_traveled[: None if number <= 0 else number]

    return scoreboard


def rchop(thestring, ending):
    """Chops the ending from string, if it matches."""
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    raise IOError('Invalid file found: "{}"'.format(thestring))


def parse_UUID(playerdata_folder):
    UUID_name_pairs = []
    for file in (entry.path for entry in scandir(playerdata_folder) if entry.is_file()):
        basename = os.path.basename(file)
        UUID = rchop(basename, '.dat')
        with create_temp(file) as nbtfile:
            playername = str(nbtfile['bukkit']['lastKnownName'])
        UUID_name_pairs.append({'UUID': UUID, 'lastKnownName': playername})
    return UUID_name_pairs


def get_time_as_str():
    UTC_now = time.gmtime()
    hour = str(UTC_now.tm_hour).zfill(2)
    minute = str(UTC_now.tm_min).zfill(2)
    return hour + minute


def parse(to_file, playerdata_folder, from_file, number):
    with create_temp(from_file) as file:
        scoreboard = parse_scores(file, number)
    UUID_name_pairs = parse_UUID(playerdata_folder)
    time_as_str = get_time_as_str()
    output = {
        'scores': scoreboard,
        'UUID': UUID_name_pairs,
        'time': time_as_str,
    }
    with open(to_file, 'w') as f:
        json.dump(output, f)


@contextmanager
def create_temp(file):
    """Copies and opens NBT file in read mode. Deletes it afterwards."""
    temp_dir = tempfile.gettempdir()
    basename = os.path.basename(file)
    temp_path = os.path.join(temp_dir, '{}.copy'.format(basename))
    shutil.copyfile(file, temp_path)
    yield nbt.NBTFile(temp_path, 'rb')
    os.remove(temp_path)


def parser():
    """Take care of parsing arguments from CLI."""
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('--n', type=int, default=0,
                            help='Number of scores to save')
    arg_parser.add_argument('--f', type=str, default='scoreboard.dat',
                            help='Name of the file to read scores from')
    arg_parser.add_argument('--t', type=str, default='top_scores.txt',
                            help='Name of the file to save scores to')
    arg_parser.add_argument('--p', type=str, default='playerdata',
                            help='Directory inside of which player data is stored')
    return arg_parser.parse_args()


def main():
    args = parser()
    tries = 5
    while tries > 0:
        try:
            parse(
                to_file=args.t,
                playerdata_folder=args.p,
                from_file=args.f,
                number=args.n
            )
        except Exception as e:
            print("Exception {}[{}] occured. Trying again {} more time{}.".format(type(e).__name__,
                                                                                  e,
                                                                                  tries,
                                                                                  's' if tries != 1 else ''),
                  file=sys.stderr)

            tries -= 1
        else:
            tries = 0


if __name__ == '__main__':
    main()
