# -*- coding: utf-8 -*-

"""Set of helper functions for text_clean.py"""

# Allow compatibility between Python 2.7 and 3.5
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from io import open 
#####

import itertools # Used to recombine n_groups into one message
import pickle # Packs and unpacks pre-stored Python objects
import re # Used to parse texts
import sys # # Checks user's Python version

import nltk # Supports a variety of NLP functions

# Set of symbols to remove
SYMBOLS = {
    '#', '[', '(', ']', '}', '_', '@', '+', ')', 
    '/', '%', '`', '>', '\\', '~', '^', '-', '&', 
    '$', '=', '*', '<', '{'
    }
           
# Set of punctuation marks to keep
PUNCTUATION = {
    '!', '"', ',', "'", ':', '.', ';', '?', '|'
    }

# Set of valid one letter words
VALID_ONE_LETTERS = {'a', 'i', 'k'}

# Check for Python 3.x
if sys.version_info.major == 3:
    # Load set of valid English digraphs
    with open('pkl_objects/3_x/english_words.pkl', 'rb') as handle:
        ENGLISH_WORDS = pickle.load(handle)
    
    # Load set of valid two letter words
    with open('pkl_objects/3_x/valid_two_letters.pkl', 'rb') as handle:
        VALID_TWO_LETTERS = pickle.load(handle)
    
    # Load set of valid consonant digraphs
    with open('pkl_objects/3_x/valid_cons_digraphs.pkl', 'rb') as handle:
        VALID_CONS_DIGRAPHS = pickle.load(handle)
     
    # Load set of valid vowel digraphs
    with open('pkl_objects/3_x/valid_vowel_digraphs.pkl', 'rb') as handle:
        VALID_VOWEL_DIGRAPHS = pickle.load(handle)

# Check for Python 2.7. 
if sys.version_info.major == 2:
    # Load set of valid English digraphs
    with open('pkl_objects/2_7/english_words.pkl', 'rb') as handle:
        ENGLISH_WORDS = pickle.load(handle)
    
    # Load set of valid two letter words
    with open('pkl_objects/2_7/valid_two_letters.pkl', 'rb') as handle:
        VALID_TWO_LETTERS = pickle.load(handle)
    
    # Load set of valid consonant digraphs
    with open('pkl_objects/2_7/valid_cons_digraphs.pkl', 'rb') as handle:
        VALID_CONS_DIGRAPHS = pickle.load(handle)
     
    # Load set of valid vowel digraphs
    with open('pkl_objects/2_7/valid_vowel_digraphs.pkl', 'rb') as handle:
        VALID_VOWEL_DIGRAPHS = pickle.load(handle)

def str_to_bool(option):
    
    """Converts True and False option strings to booleans."""
    
    if option == 'True': # String
        return True # Boolean
    elif option == 'False': # String
        return False # Boolean
    else: # Cannot proceed if values other than True or False are passed
        raise ValueError("Options can only be True or False")

def _read_input(input_file):
    
    """Reads input file and prepares text for cleaning."""
    
    # Read the full conversation into a string 
    with open(input_file, 'r', encoding='utf-8') as input_handle:
        conversation = input_handle.read()
    
    # Split the conversation into messages based on the '|' divider
    # Tokenize each message into character and punctuation tokens
    messages = [nltk.word_tokenize(message.strip()) 
                for message in conversation.split('|')]
    
    # Send messages to the cleaner method
    return messages

def _join_punctuation(cleaned_message):
    
    """Properly joins punctuation marks at the ends of words"""
    
    # Allow iteration with over the message list using "next" built-in
    cleaned_message = iter(cleaned_message)
    # Take the first token in the message list
    previous_token = next(cleaned_message)
    # Loop over each token in message list, starting from second token
    for current_token in cleaned_message:
        # Concatenate token with previous if current token has punctuation mark
        if re.search(r'[{}]'.format(".,;?!'"), current_token):
            previous_token += current_token
        # Otherwise, return previus token unchanged
        else:
            yield previous_token
            # Move to next token and repeat
            previous_token = current_token
    # Return final token unchanged since no punctuation mark can follow
    yield previous_token

def _is_a_long_string(token):
    
    """Checks if token is greater than length 13"""
    
    # Extract characters from string, ignore punctuation
    res = re.search(r'\w+', token)
    if res:
        if len(res.group()) > 13:
            return True
    return False

def _is_number(token):
    
    """Checks if token is an integer or float"""
    
    # Check for standard integer (4) or float (4.90)
    try:
        float(token)
        return True
    except ValueError:
        # Check for comma-separated integers or floats (4,900)
        if re.match(r'\d+,\d+', token):
            return True
        # Check for numbers that end in punctuation
        if re.match(r'\d+[{}]'.format(".,;?!'"), token):
            return True
        return False
    
def _is_time(token):
    
    """Special case check for HH:MM time tokens
    Used because time token fails alpha and numeric check
    E.g. "4:00".isalpha() and "4:00".isnumeric() are False
    """
    
    if re.match(r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$', token):
        return True
    return False

def _is_ordinal(token):
    
    """Special case check for ordinals
    Used because ordinals fail mixed type check
    E.g. "5th" and "101st" are considered to have mixed types (int and string)
    """
    
    if re.match(r'\d+(st|nd|rd|th)$', token):
        return True
    return False

def _has_apostrophe(token):
    
    """Special case check for tokens containing apostrophe
    Used because possessives and contractions fail alpha check
    E.g "brother's".isalpha() or "they're".isalpha() are False
    """
    
    if "'" in token:
        return True
    return False
    
def _is_mixed_type(token):
    
    """Checks if token contains mix of alpha, numeric, symbols, or punctuation"""
    
    # Keep currency special case
    if token[0] == '$' and _is_number(token[1:]):
        return False
    # Keep percentage special case
    if token[-1] == '%' and _is_number(token[:-1]):
        return False
    # Keep time token, ordinal token, and punctuation in token special cases
    if _is_time(token) or _is_ordinal(token) or _has_apostrophe(token):
        return False
    # Check if token is neither alpha nor numeric
    # Match strings with symbols as well
    # E.g. "Math123", "$John$", "Roger_Jones"
    if not token.isalpha() and not _is_number(token):
        return True
    # Otherwise, token is a normal token, such as word or number
    return False

def _has_repeating_chars(token):
    
    """Checks if token contains repeating characters, e.g. 'Repppppeat'"""
    
    # Extract characters from string, ignore punctuation
    res = re.search(r'\w+', token)
    if res:
        # Normalize case so mixed-case repeating characters are caught
        token = res.group().lower()
        # Check if three or more characters are found repeating 
        if any(token[i] == token[i - 1] and token[i] == token[i + 1]
               for i in range(1, len(token) - 1)):
            # Remove if repetition is found
            return True
    # Otherwise, keep the token
    return False
    
def _remove_n_groups(message, length):
    
    """Removes groups n words long that repeat"""
    
    # Create list of indexes to used to partition message
    indexes = [i for i in range(len(message) + 1) if i % length == 0]
    # Partition message into groups n characters long
    n_groups = [message[i: i + length] for i in indexes]
    # Start with an empty list and build up
    keep_groups = []
    # Check each group except for the last
    for i, group in enumerate(n_groups[:-1]):
        # Ignore group if it repeats
        if n_groups[i] == n_groups[i + 1]:
            continue
        # Otherwise, keep the group
        else:
            keep_groups.append(group)
    # Keep the last group
    keep_groups.append(n_groups[-1])
    # Chain groups together into one list
    keep_groups = list(itertools.chain.from_iterable(keep_groups))
    # Return groups that did not repeat
    return keep_groups

def _is_invalid_pair(pair):
    
    """Checks if a pair of English characters is invalid"""
    
    # Prepare regex pattern for consonant digraph or vowel digraph check
    pattern = r'[^aeiouy]+$|[aeiouy]+$'
    # 1.) Check if pair is consonant digraph or vowel digraph
        # Consonant / vowel digraphs are always considered valid
    # 2.) Check if pair is invalid consonant digraph
    # 3.) Check if pair is invalid vowel digraph
    if re.match(pattern, pair):
        if pair not in VALID_CONS_DIGRAPHS and pair not in VALID_VOWEL_DIGRAPHS:
            return True
    # Otherwise, token is valid
    return False

def _remove_gibberish(cleaned_message):
    
    """Removes gibberish language from a message"""
    
    # Loop over each token
    for i, token in enumerate(cleaned_message):
        # Skip over punctuation; process character strings only
        token = token.lower()
        if not token.isalpha():
            continue
        # Erase all consonant tokens
        if re.match(r'[^aeiouy]+$', token):
            cleaned_message[i] = ''
            continue
        # If token is one letter, check if invalid
        if len(token) == 1:
            if token not in VALID_ONE_LETTERS:
                # Erase if invalid; move to next
                cleaned_message[i] = ''
                continue
            else:
                # Do nothing if valid; move to next
                continue
        # If token is two letter, check if invalid
        if len(token) == 2:
            if token not in VALID_TWO_LETTERS:
                # Erase if invalid; move to next
                cleaned_message[i] = ''
                continue
            else:
                # Do nothing if valid; move to next
                continue
        # Do nothing if token is a valid English word; move to next
        if token in ENGLISH_WORDS:
            continue
        # Break token into list of pairs of characters
        # E.g. 'test' >> ['te', 'es', 'st']
        pairs = [token[j: j + 2] for j in range(len(token) - 2 + 1)]
        # Erase token if any pair is invalid
        if any(_is_invalid_pair(pair) for pair in pairs):
            cleaned_message[i] = ''
            
    # Keep tokens that were not erased
    final_message = [tok for tok in cleaned_message if tok != '']           
                
    # Return tokens that were kept
    return final_message


def _clean_message(message):
    
    """Cleans an individual message"""
    
    # Iteratively construct new message from scratch
    cleaned_message = []
    # Establish length here once so it doesn't have be computed for each token
    message_len = len(message)
    for i, token in enumerate(message):
        # Keep all punctuation tokens
        if all(char in PUNCTUATION for char in token):
            cleaned_message.append(token)
            continue
        # Stop at the second to last token
        if i < message_len - 1:
            # Check and ignore repeated instances of the same token
            # Keep only the first instance
            # E.g. "John John John" >>> "John"
            if message[i] == message[i + 1]:
                continue
            # Keep if token is a math symbol and if tokens on both sides
                # are numbers
            if token in {'+', '-', '*', '/' '='} and \
            _is_number(message[i - 1]) and _is_number(message[i + 1]):
                cleaned_message.append(token)
                continue
        # Check and ignore mixed type tokens, e.g. John23, max$$$, @nne
        # Currencies ($5.00) and percentages (10%) will be kept
        if _is_mixed_type(token):
            continue
        # Ignore strings with more than 13 characters
        if _is_a_long_string(token):
            continue
        # Check and ignore tokens with repeating characters
        # E.g. "aaaaaahhhhh", "boooom", "rrrrrrrogerrrrrr"
        if _has_repeating_chars(token):
            continue
        # If token isn't ignored by this point, keep it in the new message
        cleaned_message.append(token)
        
    # Successively remove quad-groups, tri-groups, and bi-groups
    
    if len(cleaned_message) >= 8: # Must have length of 8 minimum
        cleaned_message = _remove_n_groups(cleaned_message, 4) # Quad-groups
    
    if len(cleaned_message) >= 6: # Must have length of 6 minimum
        cleaned_message = _remove_n_groups(cleaned_message, 3) # Tri-groups
     
    if len(cleaned_message) >= 4: # Must have length of 4 minimum
        cleaned_message = _remove_n_groups(cleaned_message, 2) # Bi-groups
    
    # Remove gibberish tokens
    final_message = _remove_gibberish(cleaned_message)
        
    # Return tokens that were kept
    return final_message
    
def clean_text(current_input):
    
    """Reads messages file, splits it into individual messages, cleans each one,
    and recombines them into string of consecutive cleaned messages
    """
    
    # Fetch messages from file
    messages = _read_input(current_input)
    # Iteratively add new messages as they are generated
    cleaned_messages = []
    for message in messages:
        if not message:
        # If message contains no content, append empty message
            cleaned_message = ''
        # Otherwise, attempt cleaning the message
        else:
            cleaned_message = _clean_message(message)
        # Append each new cleaned message to the list of cleaned messages
        cleaned_messages.append(' '.join(_join_punctuation(cleaned_message)))            
    # Join each message with a divider for final output
    cleaned_messages = ' | '.join(cleaned_messages)
            
    # Return cleaned messages string to write to new file
    return cleaned_messages
