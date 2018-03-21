import argparse
import sys
import tempfile
import os
import shutil
import json

from collections import defaultdict
from nbt import nbt


def main(arguments):
    args = parse_commandline(arguments)
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'scoreboard.dat.copy')
    shutil.copyfile(args.input_file, temp_path)
    try:
        parsed_scoreboard = parse_scoreboard(args.sort,
                                             args.combined,
                                             args.input_file,
                                             )
        save_to_JSON(parsed_scoreboard,
                     args.sort,
                     args.output_file,
                     args.top,
                     args.indent,
                     )
    except Exception as e:
        print(e)
    finally:
        os.remove(temp_path)


def parse_scoreboard(sort, combined={}, file='scoreboard.dat'):
    for cname in combined.values():
        if cname not in sort:
            raise ValueError('"sort" must contain every entry from "combined"')

    nbtfile = nbt.NBTFile(file, 'rb')
    objectives = {str(tag['Name']): {}
                  for tag in nbtfile['data']['Objectives'].tags}
    player_scores = nbtfile['data']['PlayerScores']

    for score in player_scores:
        player_name = str(score['Name'])
        objective = str(score['Objective'])
        objectives[objective][player_name] = int(str(score['Score']))

    # initialize places for combined objectives
    scoreboard = {combined_name: defaultdict(int)
                  for combined_name in combined.values()}

    for key, obj in objectives.items():
        # Check if objective should be combined
        for combined_objective in combined:
            if combined_objective in key:
                for name, score in obj.items():
                    scoreboard[combined[combined_objective]][name] += score
                break
        else:
            if key in sort:
                scoreboard[key] = obj

    return scoreboard


def save_to_JSON(scoreboard,
                 sort,
                 file='top_scores.txt',
                 top_scores=0,
                 indent=None,
                 ):
    # Convert to tuples since dictionaries in JSON are not sorted
    scoreboard = {objective: sorted(
        ((name, score)
         for name, score in obj.items()),
        key=lambda x: x[1],
        reverse=sort[objective],
    )[:top_scores if top_scores != 0 else None]
        for objective, obj in scoreboard.items()
    }

    with open(file, 'w') as f:
        json.dump(scoreboard, f, indent=indent)


def parse_commandline(arguments):
    arg_parser = argparse.ArgumentParser(
        description=('Extracts top player scores '
                     'from files written in NBT format.')
    )

    arg_parser.add_argument('-s',
                            '--sort',
                            type=json.loads,
                            default={},
                            help=('Dictionary of {"name": boolean} pairs. '
                                  'If boolean = True -> scorses will be sorted'
                                  ' in descending order'),
                            )
    arg_parser.add_argument('-t',
                            '--top',
                            type=int,
                            default=0,
                            help='Number of top scores to save',
                            )
    arg_parser.add_argument('-i',
                            '--input_file',
                            type=str,
                            default='scoreboard.dat',
                            help='Path to the file to read scores from',
                            )
    arg_parser.add_argument('-o',
                            '--output_file',
                            type=str,
                            default='top_scores.txt',
                            help='Path of the file to save scores to',
                            )
    arg_parser.add_argument('-c',
                            '--combined',
                            type=json.loads,
                            default={},
                            help='Dictionary of {"pattern": "new_name"} pairs',
                            )
    arg_parser.add_argument('--indent',
                            type=int,
                            default=0,
                            help=('Indentation level, helpfull if output file'
                                  'will be read by human. '
                                  'Use 0 to decrease size'),
                            )
    arg_parser.add_argument('-c',
                            '--config',
                            type=str,
                            help=('Path to config file'),
                            )
    arg_parser.add_argument('--all',
                            action='store_true',
                            help='If it\'s present, extracts all objectives',
                            )
    # TODO: Add following arguments:
    """
        --input_file str
        --output_file str
        --combined {'pattern': 'new_name'}
        --sort {'name': 'a'|'d', ...}
        --group_by str('player'|'objective') # defaults to 'objective'
        --indent int # indent in JSON, defaults to None
        --top_scores int # top scores to save, defaults to 0 which means all
    """
    return arg_parser.parse_args(arguments)


# TODO add class that always return's True when chenking 'x in class'
# and 'class[x]' always returns same thing (i.e. False)
# This is to simulate arg.sort when '--all' flag is set


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
