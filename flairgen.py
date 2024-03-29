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
import csv
from itertools import product, chain

##] Import image library to generate sprites
import Image

##] Import reddit related libraries
import praw as reddit # Python Reddit API Wrapper

##] Super cool variables
CONFIG_FILE = "settings.json"
COOKIE_FILE = "reddit.cookie"
FLAIR_CSV_FILE = "output/flair.csv"
FLAIR_IMG_FILE = "output/flair.png"
FLAIR_CSS_FILE = "output/flair.css"
#PNG_METADATA = 

FLAIRGEN_START_BLOCK = "/***** [{{FLAIRGEN START DO NOT TOUCH}}] *****/"
FLAIRGEN_END_BLOCK = "/***** [{{FLAIRGEN END DO NOT TOUCH}}] *****/"

CSS_HEADER = """{1}
/**
 * CSS sprite code generated by Fluxflashor's Flair Generator
 * http://github.com/Fluxflashor/flairgen
 * Generated at: {0}
 **/
""".format(time.time(), FLAIRGEN_START_BLOCK)

CSS_FOOTER = """
/* End of CSS sprites */
{0} 
""".format(FLAIRGEN_END_BLOCK)

HELP_TEXT = '''
  flairgen.py <option>
  
  Valid Options for flairgen.py
  ------------------------------------------------------------------------
    GENERATE: creates sexy css and css sprite of flair
              also makes a csv file for it
      UPLOAD: pushes the upload to reddit. will ask for credentials
        HELP: gives you this junk'''

r = reddit.Reddit(user_agent="Fluxflashor's Flairgenerator Tool flairgen.py - github/fluxflashor/flairgen")

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
    return [(r[0], r[1], r[2]) for r in f]


def generate_flair(csv_file_out, img_file_out, css_file_out):
     
    ##] Read configuration file, store in variable
    jconfig = read_config(CONFIG_FILE)

    ##] Create a huge container to store all the flair inside
    ##] We will crop it when the image is finished
    ##] Container should be able to fit 300 sprites based
    ##] on the filesize.
    column_width, row_height = int(jconfig['config']['column_width']), int(jconfig['config']['row_height'])
    num_of_cols = len(jconfig['images'])
    image_width, image_height = column_width * num_of_cols, row_height * 300

    css_sprite = Image.new("RGBA", (image_width, image_height))

    css_file = open(css_file_out, "w")
    css_file.write(CSS_HEADER)

    ##] items_list is a list of lists. each list inside
    ##] of the list is a list of the items from the 
    ##] appropriate category.
    items_list = []

    ##] css_classes is a list that contains all of our
    ##] generated css classes that will be saved to our
    ##] csv file for importing into the redditapi
    css_classes = []

    ##] To help us keep track of positioning
    sprite_row = 1

    
    sprite_images = {}
    for category in jconfig['images']:
        ##] For each one of our custom categories,
        ##] We have a different column of our sprite
        ##] image.
        temp_list = []
        
        
        for item, image_path in jconfig['images'][category].iteritems():
            ##] This will allow users to select a flair
            ##] that is made up of only one image and not
            ##] multiple images. For the WoW Reddit, this
            ##] allows people to only represent Paladins,
            ##] or only represent the Horde.
            css_classes.append(item)
            
            ##] Add the item to our temp_list so we can
            ##] store it in our items_list when we are finished iterating.
            temp_list.append(item)

            ##] Since this is our single image only column
            ##] We need to create a spacer infront of it so
            ##] the image is beside the persons name.
            ##] This only works for Left sided flair atm
            ##] Add the current flair to our image

            sprite_images[item] = Image.open(image_path)

            #current_image = Image.open(image_path)
            image_width, image_height = sprite_images[item].size
            css_sprite.paste(sprite_images[item], (0, sprite_row * row_height - row_height))

            ##] Generate CSS for the current item
            ##] Example of a css rule for each flair
            ##] .flair-paladin:after {
            ##]   content: "";
            ##]   background-position: 0px -80px;
            ##]   width: 18px
            ##] }
            #print sprite_row * row_height - row_height
            css = ".flair-{0}:after{{ content: \"\"; background-position: {1}px -{2}px; width: {3}px;}}\n".format(item, "0", sprite_row * row_height - row_height, column_width)
            css_file.write(css)

            sprite_row += 1


        ##] Store the list of items from this particular
        ##] category inside of a list so that we can use it
        ##] to generate combinations for our flair sprites
        items_list.append(temp_list)

    ##] This generates all possible flair combinations each
    ##] of our different categories. For the WoW Reddit,
    ##] category one is a faction and category two is a the
    ##] classes. Faction is the first flair image
    ##] and Class is the second flair image.

    #[list(r) for r in zip(*items_list)]
    #print r[1]
        #print zip(*items_list)

#    for r in product(*items_list):
        ##] Add the current flair piece to a list of CSS Classes
 #       flair_class = "-".join(r)
  #      css_classes.append(flair_class)

        ##] Add the current flair to the CSS file
   #     css = ".flair-{0}:after{{ content: \"\"; background-position: {1}px -{2}px; width: {3}px; }}\n".format(flair_class, "0", sprite_row * row_height - row_height, column_width * num_of_cols)
    #    css_file.write(css)

        ##] Add the current flair piece to our CSS Sprite image
     #   derp = 0
      #  for item in r:
       #     image_width, image_height = sprite_images[str(item)].size
        #    css_sprite.paste(sprite_images[item], (derp * column_width, sprite_row * row_height - row_height))
         #   derp += 1

        #sprite_row += 1

    
    ##] Apply the CSS File footer and close it
    css_file.write(CSS_FOOTER)
    css_file.close()

    ##] Crop the CSS Sprite
    cropped_sprite = css_sprite.crop((0, 0, num_of_cols * column_width, sprite_row * row_height))

    ##] Save the CSS Sprite Image
    cropped_sprite.save(img_file_out)

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

    ##] Retrieve flair templates from the csv file
    flair_templates = flair_from_csv(csv_file)
    
    for template in flair_templates:
    	print "Adding Flair Template {0} to /r/{1}".format(template[1], subreddit)
        r.get_subreddit(subreddit).add_flair_template(template[0], template[1], template[2])


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
            generate_flair(FLAIR_CSV_FILE, FLAIR_IMG_FILE, FLAIR_CSS_FILE)

        elif option == "UPLOAD":
            upload_flair(FLAIR_CSV_FILE)

        elif option == "HELP":
            print HELP_TEXT

        else:
            print "Oh God How Did This Get Here I Am Not Good With Computer\nNo seriously.. what the hell? This should never trigger"
    
    else:
        print HELP_TEXT



if __name__ == '__main__':
    main()


