"""
Extracts top player scores from files written in NBT format.
Written by Prof_Bloodstone (aka B1o0dy) for use at Near Vanilla server.
"""
from __future__ import division

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
import traceback
from collections import namedtuple, defaultdict, ChainMap
from contextlib import contextmanager

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
COMBINE_OBJ = namedtuple('COMBINE_OBJ', 'regex, new_name')


def extract_scores(nbtfile):
    """Extract scores from nbt file and convert to python format that is easier to work with."""
    objectives = {tag['Name'].value: {'DisplayName': json.loads(tag['DisplayName'].value)['text'], 'scores': []}
                  for tag in nbtfile['data']['Objectives'].tags}

    player_scores = nbtfile['data']['PlayerScores']

    for score in player_scores:
        player_name = score['Name'].value
        objective = score['Objective'].value
        value = score['Score'].value
        objectives[objective]['scores'].append(PLAYER_SCORE(player_name, value))

    return objectives


def combine_scores(objectives, to_combine, delete_combined=False):
    combined_objectives = defaultdict(lambda: defaultdict(int))
    for key, obj in objectives.items():
        new_name = next((name for regex, name in to_combine if regex.search(key) is not None), None)
        if new_name is not None:
            for player in obj['scores']:
                combined_objectives[new_name][player.name] += player.score
        if delete_combined:
            del objectives[key]

    return {obj_name: {'DisplayName': obj_name,
                       'scores': [PLAYER_SCORE(player_name, score)
                                  for player_name, score in obj.items()]}
            for obj_name, obj in combined_objectives.items()}


def sort_scores(objectives, descending, reverse):
    for key, obj in objectives.items():
        sort_descending = descending if key not in reverse else not descending
        obj['scores'].sort(key=lambda x: (-x.score if sort_descending else x.score, x.name))


def get_scores(from_file, combine, sort, reverse, number, blacklist, delete_combined):
    with create_temp(from_file) as file:
        objectives = extract_scores(file)

    combined_scores = combine_scores(objectives, combine, delete_combined)
    scores = dict(ChainMap(combined_scores, objectives))
    sort_scores(scores, sort, reverse)

    if number > 0:
        for key, obj in scores.items():
            scores[key]['scores'] = obj['scores'][:number]

    for key, obj in scores.items():
        scores[key]['scores'] = [{'index': index, 'playerName': entry.name, 'score': entry.score}
                                 for index, entry in enumerate(obj['scores'], start=1)]

    return {key: value for key, value in scores.items() if key not in blacklist}


def rchop(thestring, ending):
    """Chops the ending from string, if it matches."""
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    raise IOError('Invalid file found: "{}"'.format(thestring))


def get_UUID_with_names(playerdata_folder):
    UUID_name_pairs = []
    for file in (entry.path for entry in scandir(playerdata_folder) if entry.is_file()):
        basename = os.path.basename(file)
        UUID = rchop(basename, '.dat')
        with create_temp(file) as nbtfile:
            playername = str(nbtfile['bukkit']['lastKnownName'])
        UUID_name_pairs.append({'UUID': UUID, 'lastKnownName': playername})
    return UUID_name_pairs


def extract_and_save_data(args):
    from_file = args['input_file']
    to_file = args['output_file']
    playerdata_folder = args['playerdata']
    number = args['number']
    combine = args['combine']
    reverse = args['reverse']
    sort = args['sort_descending']
    blacklist = args['blacklist']
    delete_combined = args['delete_combined']

    output = {'timestamp': time.time(),
              'scores': get_scores(from_file, combine, sort, reverse, number, blacklist, delete_combined)}

    if playerdata_folder is not None:
        output['UUID'] = get_UUID_with_names(playerdata_folder)

    with open(to_file, 'w') as f:
        json.dump(output, f)


@contextmanager
def create_temp(file):
    """Copies and opens NBT file in read mode. Deletes it afterwards."""
    temp_dir = tempfile.gettempdir()
    basename = os.path.basename(file)
    temp_path = os.path.join(temp_dir, '{}.copy'.format(basename))
    shutil.copyfile(file, temp_path)
    try:
        yield nbt.NBTFile(temp_path, 'rb')
    finally:
        os.remove(temp_path)


def parser():
    """Take care of parsing arguments from CLI and config file, if provided."""

    defaults = {
        'number': 0,
        'input_file': 'scoreboard.dat',
        'output_file': 'top_scores.txt',
        'sort_descending': True,
        'reverse': [],
        'combine': [],
        'blacklist': [],
        'delete_combined': False
    }

    arg_parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)

    arg_parser.add_argument('-n', '--number', type=int,
                            help='Number of scores to save.\n'
                                 'If <= 0, all scores will be saved'
                                 ' [DEFAULT {}]'.format(defaults['number']))

    arg_parser.add_argument('-i', '--input', '--scoreboard', dest='input_file', type=str,
                            help='Name of the file to read scores from [DEFAULT {}]'.format(defaults['input_file']))

    arg_parser.add_argument('-t', '--output', '--top', dest='output_file', type=str,
                            help='Name of the file to save scores to [DEFAULT {}]'.format(defaults['output_file']))

    arg_parser.add_argument('-p', '--playerdata', type=str,
                            help='Directory inside of which player data is stored, used to extract UUID and names.\n'
                                 'Need to be running Spigot/Bukkit for it to work!')

    arg_parser.add_argument('-a', '--ascending', action='store_false',
                            help='Flag indicating that scoreboard should be sorted in ascending order by default')

    arg_parser.add_argument('-d', '--descending', action='store_true',
                            help='Flag indicating that scoreboard should be sorted in descending order by default [DEFAULT]')

    arg_parser.set_defaults(ascending=None, descending=None)

    arg_parser.add_argument('-r', '--reverse', action='append',
                            help='List of all objective names which should be sorted in the opposite direction to the'
                                 ' direction chosen by "ascending" / "descending" arguments.\n'
                                 'Has to be repeated for every item added!\n'
                                 'Example: "-r obj1 -r obj2 -r obj3"')

    arg_parser.add_argument('--combine', action='append',
                            help='List of all objective names which should be combined into one.\n'
                                 'Have a form of regular expression and new name separated by a space "regex name"\n'
                                 'Has to be repeated for every item added!\n'
                                 'Example: "--combine distance\ total_traveled" will combine every scoreboard with name "distance" in them and save it into "total_traveled"')

    arg_parser.add_argument('-c', '--config', dest='config_file', type=str,
                            help='File containing configuration. CLI arguments override it!')

    arg_parser.add_argument('-b', '--blacklist', action='append',
                            help='List of all objective names which shouldn\'t be in the output file\n'
                                 'Has to be repeated for every item added!\n'
                                 'Example: "-b obj1 -b obj2 -b obj3"')

    arg_parser.add_argument('--delete_combined', action='store_true',
                            help='Flag indicating that source scoreboards used for combining should be deleted\n'
                                 'By default they don\'t get deleted')

    cli_args = arg_parser.parse_args()

    if None not in (cli_args.ascending, cli_args.descending):
        raise argparse.ArgumentError('Can\'t provide both "ascending" and "descending" arguments!')

    cli_args.sort_descending = next(item for item in
                                    (cli_args.ascending, cli_args.descending, defaults['sort_descending'])
                                    if item is not None)

    config_args = {}

    if cli_args.config_file is not None:
        with open(cli_args.config_file, 'r') as f:
            config_args = json.load(f)
            if config_args.get('combine') is not None:
                config_args['combine'] = [COMBINE_OBJ(re.compile(item['regex']), item['new_name'])
                                          for item in config_args['combine']]

        del cli_args.config_file

    if cli_args.combine is not None:
        cli_args.combine = [COMBINE_OBJ(re.compile(regex), name) for regex, name in
                            (s.split(maxsplit=1) for s in cli_args.combine)]

    cli_args_dict = {key: value for key, value in vars(cli_args).items() if value is not None}

    # TODO translate config names to accept the same as CLI

    return ChainMap(cli_args_dict, config_args, defaults, defaultdict(lambda: None))


def main():
    args = parser()

    tries = 3
    while tries > 0:
        try:
            extract_and_save_data(args)
        except Exception as e:
            tries -= 1
            print("Exception {} occured. Trying again {} more time{}.\n{}"
                  .format(type(e).__name__, tries, 's' if tries != 1 else '', traceback.format_exc()),
                  file=sys.stderr)
        else:
            tries = 0


if __name__ == '__main__':
    main()
