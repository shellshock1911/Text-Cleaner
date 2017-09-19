#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""This script automates text cleaning over one or more text files.
   Input should consist one or more messages separated by '|' dividers
   
   Run the following at the Terminal prompt to get started for Python 2.7:
    
    $ python text_clean.py --input example_texts
    
       or (for Python 3.x)
       
    $ python3 text_clean.py --input example_texts
    
   
   Currently the following cleaning functions are supported for
   each message in the text file:
       
1.) Repeating tokens are removed; first instance is kept:
    >>> "I am John John John" becomes "I am John"
    
2.) Mixed type tokens are removed, e.g. "John23", "$Max$", however some special
    cases are kept:
        
      >>> Dollars ($5, $5,000)
      >>> Percentages (2%, 2,000%)
      >>> HH:MM Times (4:00, 17:00)
      >>> Ordinals (5th, 22nd, 33rd, 71st)
      >>> Punctuation at end of token (Hello!, Yes?, Jacks', 101,)
      >>> Apostrophe tokens (Don't, Didn't, Jack's)
      
3.) Long tokens are removed (character string length greater than 13)
    
4.) Tokens with three or more repeating characters are removed:
    >>> "Roggggerrrrrr, 1000000000" 
    
5.) All non-punctuation symbols are removed (@, ^, #, etc.), however math 
    expressions are kept (2 + 2, 5 * 5, 7 - 7 = 0)
    
6) Repeating quad-groups, tri-groups, and bi-groups are removed; first
   instance is kept:
   >>> "I am watching I am watching I am watching I am watching" becomes
       "I am watching"
"""

# Allow compatibility between Python 2.7 and 3.5
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from io import open 
#####

import glob # Allows batch input file fetching
import os   # Allows convenient file handling
import time # Calculates script runtime
import text_clean_utils # Collection of helper functions in utils file

# Allows parsing of user-specified options at script call
from optparse import OptionParser 

# Initialize parser, then add arguments. Input directory is required. 
PARSER = OptionParser()

PARSER.add_option('-i', '--input', dest='input_directory',
                  help='input directory with files that need text cleaning')
PARSER.add_option('-v', '--verbose', dest='verbose', default="True",
                  help='toggle console output')

OPTIONS, _ = PARSER.parse_args() # Convert options into usable strings

# Load user options into global constants for use in the script
INPUT_DIR = OPTIONS.input_directory # Directory containing input files (required)
VERBOSE = OPTIONS.verbose # Display console output (optional)

# Ensure input directory exists, otherwise the script exits
assert os.path.isdir(INPUT_DIR), \
        "The input directory doesn't exist in the working directory"

# Default name for output directory, change if needed
OUTPUT_DIR = 'cleaned_output'  
# Check if output directory exists, otherwise create one
if not os.path.isdir(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
    
##### Main Function #####
def clean_text(input_dir, verbose='True'):

    """Takes an input directory and processes all .txt files within, cleaning
    all contents within each one. Outputs to a separate directory cleaned 
    messages in files with the --CLEANED flag
    
    `input_dir` = name of directory that contains input .txt files
    `verbose` = toggles console output (default True)   
    """
    
    start_time = time.time() # Start runtime
    
    # Set verbose flag for use throughout
    verbose = text_clean_utils.str_to_bool(verbose)

    # Initialize generator that fetches message files one by one
    messages_fetcher = glob.iglob('{}/*.txt'.format(input_dir))
    
    # Begin script
    if verbose:
        print("\n------------------------------\n"
              "Text cleaning starting\n"
              "------------------------------\n")
    
    attempted_files = 0 # Track how many files attempted conversion
    completed_files = 0 # Track how many files converted successfully
    
    # Main loop that batch processes input files 
    while messages_fetcher:
        try:
            current_messages_file = next(messages_fetcher) # Fetch next messages file
        except StopIteration:
            break # Execute when there are no more files to fetch

        # Create a path for the output file in the output directory
        # Flag each output file with '--CLEANED', indicating that any
            # messy text has been found and cleaned
        new_messages_file = os.path.join(OUTPUT_DIR, '{0}--CLEANED{1}'.format(
            *os.path.splitext(os.path.basename(current_messages_file))))

        attempted_files += 1 # Increment prior to processing

        # Clean all messages in current_messages_file
        cleaned_messages = text_clean_utils.clean_text(current_messages_file)
       
        # Write new messages to file in output directory at the path
            # specified in current_output variable
        with open(new_messages_file, 'w', encoding='utf-8') as file_handle:
            file_handle.write(cleaned_messages)
        # Display where current output file is located on the local file system
        if verbose:
            print("*".rjust(5), "\t", current_messages_file, ">>>", new_messages_file)

        # Increment upon successful processing of current input file
        completed_files += 1

    # Main loop ends
    end_time = time.time() # Runtime ends

    # Output Report
    if verbose:
        print("\n--------------------------------------------\n"
              "Text cleaning complete\n"
              "{0} of {1} files cleaned in {2} minutes\n"
              "--------------------------------------------\n".format(
                  completed_files, attempted_files, round((
                      end_time - start_time) / 60, 3)))
        
    # Exit
    return

# Standard code that allows the file to be run as a script from the terminal   
if __name__ == '__main__':
    clean_text(INPUT_DIR, verbose=VERBOSE)
