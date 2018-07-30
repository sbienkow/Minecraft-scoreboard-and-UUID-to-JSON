Extract scoreboard (and UUID with names) to JSON.

##What is it? 
It's a simple python script that can extract scoreboards from NBT file and convert them to json. It has some configuration options, allowing you to sort, combine and filter objectives. 

##Why? 
We wanted to display highscores on the site and json is easy to use in JS, so…  
You can see it working here: [nearvanilla.com](https://nearvanilla.com/highscores.html) 

##How to run it? 
I highly recommend using python3 in a virtual environment. 

Download this repository - or at least requirements.txt and python script. 
#####Install needed packages
`pip3 install -r requirements.txt`
#####Run the script
`python3 mc_NBT_top_scores.py --help`  
See “Usage” below for all available options. 

If you want to run this every X hours / minutes / seconds /… I recommend using Cron or some similar scheduler. 

##Contributing
###Help! It's broken! 
If you think something doesn't work properly, create an issue on github. 

###I have an idea for a feature! 
Cool! Create an issue on github and I'll take a look at it. 

###I added a feature! 
Please share it by making a pull request. I'll take a look at it and might merge it. 

##Usage
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
                        Example: `--combine “distance total_traveled”` will combine every scoreboard with name "distance" in them and save it into "total_traveled"
  -c CONFIG_FILE, --config CONFIG_FILE
                        File containing configuration. CLI arguments override it!
  -b BLACKLIST, --blacklist BLACKLIST
                        List of all objective names which shouldn't be in the output file
                        Has to be repeated for every item added!
                        Example: "-b obj1 -b obj2 -b obj3"
  --delete-combined     Flag indicating that source scoreboards used for combining should be deleted
                        By default they don't get deleted
```

