#!/usr/bin/python
#-------------------------------------------------------------------------------------
#     Package: flairgen
#      Author: Robert "Fluxflashor" Veitch
# Description: Generates Flair Sprites & CSS for a subreddit based on a config file
#       Usage: gen.py <option>
#       Notes: Developed for Python 2.7
#-------------------------------------------------------------------------------------

import sys
import json
import time
import getpass
from itertools import product

##] Import image library to generate sprites
from PIL import Image

##] Import reddit related libraries
import praw as reddit # Python Reddit API Wrapper

##] Super cool variables
CONFIG_FILE = "settings.json"
COOKIE_FILE = "reddit.cookie"
FLAIR_CSV_FILE = "output/flair.csv"
FLAIR_IMG_FILE = "output/flair.png"
#PNG_METADATA = 

r = reddit.Reddit(user_agent="Fluxflashor's Flairgenerator Tool flairgen.py - github/fluxflashor/flairgen")

HELP_TEXT = '''
  flairgen.py <option>
  
  Valid Options for flairgen.py
  ------------------------------------------------------------------------
    GENERATE: creates sexy css and css sprite of flair
              also makes a csv file for it
      UPLOAD: pushes the upload to reddit. will ask for credentials
        HELP: gives you this junk'''

##] Legit program stuff

def read_config(path):
    # First we need to open the configuration file
    try:
        config_file = open(path)
        try:
            config = json.loads(config_file.read())
        except ValueError as e:
            print "Fatal Error: Format error with configuration file.\n  ValueError: {0}".format(e)
            sys.exit()

    except IOError as e:
        print "Fatal Error: Unable to open config file. Does it exist?\n  IOError: {0}".format(e)
        sys.exit()
    else:
        config_file.close()

    return config


def login():
    username = raw_input("Reddit Username: ")
    password = getpass.getpass("Reddit Password: ")
    credentials = dict(username=username, password=password)
    return credentials


def get_subreddit():
    subreddit = raw_input("Subreddit: ")
    return subreddit


def flair_from_csv(path):
    f = csv.reader(file(path))
    # skip header row
    f.next()
    return dict((r[0], (r[1], r[2])) for r in f if r[1] or r[2])


def generate_flair(csv_file_out, img_file_out):
     
    ##] Read configuration file, store in variable
    jconfig = read_config(CONFIG_FILE)

    ##] items_list is a list of lists. each list inside
    ##] of the list is a list of the items from the 
    ##] appropriate category.
    items_list = []

    ##] css_classes is a list that contains all of our
    ##] generated css classes that will be saved to our
    ##] csv file for importing into the redditapi
    css_classes = []

    for category in jconfig['images']:
        ##] For each one of our custom categories,
        ##] We have a different column of our sprite
        ##] image.
        temp_list = []
        for item in jconfig['images'][category]:
        	##] This will allow users to select a flair
        	##] that is made up of only one image and not
        	##] multiple images. For the WoW Reddit, this
        	##] allows people to only represent Paladins,
        	##] or only represent the Horde.
            css_classes.append(item)
            
            ##] Add the item to our temp_list so we can
            ##] store it in our items_list when we are finished iterating.
            temp_list.append(item)

        ##] Store the list of items from this particular
        ##] category inside of a list so that we can use it
        ##] to generate combinations for our flair sprites
        items_list.append(temp_list)

    ##] This generates all possible flair combinations each
    ##] of our different categories. For the WoW Reddit,
    ##] category one is a faction and category two is a the
    ##] classes. Faction is the first flair image
    ##] and Class is the second flair image.
    for r in product(*items_list):
    	##] Add the current flair piece to a list of CSS Classes
        css_classes.append("{0}-{1}".format(r[0], r[1]))

        ##] Add the current flair piece to our CSS Sprite image

    ##] Save the CSS Sprite Image


    ##] Write all of our Flair CSS Classes to our CSV file for easy import through redditapi
    flair_csv = open(csv_file_out, "w")

    for css_class in css_classes:
        flair_csv.write(",{0},False\n".format(css_class))

    flair_csv.close()




def upload_flair(csv_file):

    ##] Login to reddit
    credentials = login()
    r.login(**credentials)

    ##] Select a subreddit
    subreddit = get_subreddit()

    ##] Get rid of old flair templates
    r.get_subreddit(subreddit).clear_flair_templates()

    ##] Upload all our flair templates
    flair_templates = flair_from_csv(FLAIR_CSV_FILE)

    #for template in flair_templates:
    #    r.get_subreddit().add_flair_template(text='editable', css_class='foo', text_editable=True)


def main():

    ##] Keep it simple
    if len(sys.argv) < 2:
        option = "HELP"
    else:
        option = sys.argv[1].upper()


    ##] Check if the desired function is available
    available_options = ["GENERATE", "UPLOAD", "HELP"]
    option_is_available = False

    for o in available_options:
        if option == o:
            option_is_available = True

    if option_is_available:

        if option == "GENERATE":
            print "Generating Flair"
            generate_flair(FLAIR_CSV_FILE, FLAIR_IMG_FILE)

        elif option == "UPLOAD":
            upload_flair()

        elif option == "HELP":
            print HELP_TEXT

        else:
            print "Oh God How Did This Get Here I Am Not Good With Computer\nNo seriously.. what the hell? This should never trigger"
    
    else:
        print HELP_TEXT



if __name__ == '__main__':
    main()


