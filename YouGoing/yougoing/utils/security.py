'''
Created on 26.5.2011

@author: MuZeR
'''
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
    
def get_logged_in_user():
    return None