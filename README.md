# Text Cleaner

This script automates text cleaning over one or more text files.
Input should consist one or more messages separated by pipe dividers ('|').
   
Run the following at the Terminal prompt to get started for Python 2.7:
    
    $ python2 text_clean.py --input example_texts
    
  or (for Python 3.x):
       
    $ python3 text_clean.py --input example_texts
    
-------------------------------

The core spell correcting function requires the Python nltk package.
In order to install this in your current environment, input the following at
your Terminal prompt:
    
    $ pip install nltk

-------------------------------

Currently the following cleaning functions are supported for
each message in the text file:
       
1.) Repeating tokens are removed; first instance is kept:

  - "I am John John John" >>> "I am John"
    
2.) Mixed type tokens are removed, e.g. "John23", "$Max$", however some special
    cases are kept: 

  - Dollars ($5, $5,000)
  - Percentages (2%, 2,000%)
  - HH:MM Times (4:00, 17:00)
  - Ordinals (5th, 22nd, 33rd, 71st)
  - Punctuation at end of token (Hello!, Yes?, Jacks', 101,)
  - Apostrophe tokens (Don't, Didn't, Jack's)
      
3.) Long tokens are removed (character string length greater than 13):

  - "1234567890123455" 
  - "nowthishereisareallylongword"

4.) Tokens with three or more repeating characters are removed:

  - "Rogggger"
  - "1000000" 
    
5.) All non-punctuation symbols are removed (@, ^, #, etc.), however math 
    expressions are kept:

  - "2 + 2"
  - "5 * 5"
  - "7 - 7 = 0"
    
6.) Repeating quad-groups, tri-groups, and bi-groups are removed; first
   instance is kept:

  - "I am watching I am watching I am watching I am watching" >>> ""I am watching"

7.) Gibberish tokens are removed (this is based on the author's subjective discretion):

  - "alskdjfaasdlfjkasd"
  - "s"
  - "iaaiuuuuwu"
