'''
Created on 26.5.2011

@author: MuZeR
'''
import random
import os
import settings


RANDOM_STRING_CHARS = u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!\"#&/()=?;:<>_{[]},.-*"
RANDOM_STRING_ALPHANUM = u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def generate_random_string(max_length, min_length = 1, only_alphanum = False):
    """
        Generate random salt string
    """
    salt_length = random.randint(min_length, max_length)
    if only_alphanum:
        RANDOM_STRING_ALPHABETS = RANDOM_STRING_ALPHANUM
    else:
        RANDOM_STRING_ALPHABETS = RANDOM_STRING_CHARS

    try:
        random_string = u''
        num_of_chars = len(RANDOM_STRING_ALPHABETS)
        for c in os.urandom(salt_length):
            random_string += (RANDOM_STRING_ALPHABETS[ord(c) % num_of_chars])
        return random_string
    except NotImplementedError:
        print "Urandom could not be used"
        return u''.join(random.choice(RANDOM_STRING_ALPHABETS.letters) for i in xrange(salt_length))
    
def check_password_complexity(password):
    num_of_numbers = 0
    num_of_lower_case = 0
    num_of_upper_case = 0
    num_of_special = 0
    for c in password:
        if c.isdigit():
            num_of_numbers += 1
        elif c.islower():
            num_of_lower_case += 1
        elif c.isupper():
            num_of_upper_case += 1
        else:
            num_of_special += 1
    if (num_of_numbers > 0 or num_of_special > 0) and num_of_lower_case > 0 and num_of_upper_case > 0:
        return True
    else:
        return False
    
def get_logged_in_user(request):
    return request.user
