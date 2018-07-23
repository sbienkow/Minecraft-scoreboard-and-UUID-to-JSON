Extract scoreboard (and UUID with names) to JSON.



```
usage: mc_NBT_top_scores.py [-h] [-n NUMBER] [-i INPUT_FILE] [-t OUTPUT_FILE]
                            [-p PLAYERDATA] [-a] [-d] [-r REVERSE]
                            [--combine COMBINE] [-c CONFIG_FILE]
                            [-b BLACKLIST] [--delete-combined]

Extracts top player scores from files written in NBT format.
Written by Prof_Bloodstone (aka B1o0dy) for use at Near Vanilla server.

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        Number of scores to save.
                        If <= 0, all scores will be saved [DEFAULT 0]
  -i INPUT_FILE, --input INPUT_FILE, --scoreboard INPUT_FILE
                        Name of the file to read scores from [DEFAULT scoreboard.dat]
  -t OUTPUT_FILE, --output OUTPUT_FILE, --top OUTPUT_FILE
                        Name of the file to save scores to [DEFAULT top_scores.txt]
  -p PLAYERDATA, --playerdata PLAYERDATA
                        Directory inside of which player data is stored, used to extract UUID and names.
                        Need to be running Spigot/Bukkit for it to work!
  -a, --ascending       Flag indicating that scoreboard should be sorted in ascending order by default
  -d, --descending      Flag indicating that scoreboard should be sorted in descending order by default [DEFAULT]
  -r REVERSE, --reverse REVERSE
                        List of all objective names which should be sorted in the opposite direction to the direction chosen by "ascending" / "descending" arguments.
                        Has to be repeated for every item added!
                        Example: "-r obj1 -r obj2 -r obj3"
  --combine COMBINE     List of all objective names which should be combined into one.
                        Have a form of regular expression and new name separated by a space "regex name"
                        Has to be repeated for every item added!
                        Example: "--combine distance\ total_traveled" will combine every scoreboard with name "distance" in them and save it into "total_traveled"
  -c CONFIG_FILE, --config CONFIG_FILE
                        File containing configuration. CLI arguments override it!
  -b BLACKLIST, --blacklist BLACKLIST
                        List of all objective names which shouldn't be in the output file
                        Has to be repeated for every item added!
                        Example: "-b obj1 -b obj2 -b obj3"
  --delete-combined     Flag indicating that source scoreboards used for combining should be deleted
                        By default they don't get deleted
```
