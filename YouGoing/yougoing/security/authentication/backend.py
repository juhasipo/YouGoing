"""
Inspired by Monkey-patch SHA-256
https://gist.github.com/622519
"""
import hashlib
import settings

from yougoing.utils.security import generate_random_string
from django.contrib.auth import models as django_models
from django.contrib.auth.backends import ModelBackend


def _hash_password(password,salt):
    """
        Generate a string that changes each time user logs in.
        This will make using rainbow tables harder since each username/password
        combination needs its own rainbow table.
        I might have gotten a bit too carried away with the salt, but at least
        it should be relatevily secure due to random part and changing part.
        Used some knowledge of Stack Overflow and couple of blog post discussions
        when implementing the hashing scheme:
         http://www.codinghorror.com/blog/2007/09/youre-probably-storing-passwords-incorrectly.html
         http://www.codinghorror.com/blog/2007/09/rainbow-hash-cracking.html
         http://stackoverflow.com/questions/674904/salting-your-password-best-practices
         http://stackoverflow.com/questions/536584/non-random-salt-for-password-hashes/536756#536756
    """
    print "Start hashing"
    # Salt the password with user specific data and random data
    # it will make dictionary attacks impossible, brute forcing very difficult and
    # rainbow tables are need to be regenerated after each login in order to work
    string_to_hash = settings.STATIC_SALT + unicode(password) + u":" + u":" + salt
    hasher1 = hashlib.sha256()
    hasher1.update(string_to_hash)
    hash1 = hasher1.hexdigest()
    
    # Obfuscate the real password hash with new hash in which there
    # is also long salt string.
    hash_to_hash = hash1
    for i in xrange(settings.HASH_ROUNDS):
        hash_to_hash = salt + u"$" + hash_to_hash + settings.STATIC_SALT
        hasher2 = hashlib.sha256()
        hasher2.update(hash_to_hash)
        final_hash = hasher2.hexdigest()
    print "Hash calculated: " + final_hash
    return final_hash

    
def _gen_random_salt():
    return generate_random_string(settings.SALT_MAX_LENGTH, settings.SALT_MIN_LENGTH)

#Override Django's password hashing and setter methods
def get_hexdigest(algorithm, salt, raw_password):
    if algorithm == 'sha256':
        return _hash_password( raw_password, salt )
    else:
        return get_hexdigest_old( algorithm, salt, raw_password )
get_hexdigest_old = django_models.get_hexdigest
django_models.get_hexdigest = get_hexdigest


def set_password(self, raw_password):
    """Set SHA-256 password."""
    algorithm = 'sha256'
    salt = _gen_random_salt()
    hash = get_hexdigest( algorithm, salt, raw_password) 
    self.password = '$'.join((algorithm, salt, hash))  
django_models.User.set_password = set_password

class Sha256Auth(ModelBackend):
    pass
