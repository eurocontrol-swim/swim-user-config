"""
Copyright 2019 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open Source Initiative:
http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""
import argparse
import json
import os
import sys
import hashlib
import uuid
from getpass import getpass

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

__author__ = "EUROCONTROL (SWIM)"

MIN_PASSWORD_LENGTH = 10


def _get_input_method():
    """
    Distinguish python versions and return the input method for raw input
    :return: callable
    """
    try:
        return __builtins__.raw_input
    except AttributeError:
        return input


def get_pwned_password_range(password_sha1_prefix):
    """
    Retrieves a range of sha1 pwned passwords from haveibeenpwned API whose 5 first characters match with the provided
    sha1 prefix.

    :param password_sha1_prefix: must be 5 characters long
    :type
 str    :return: list of str
    """
    response = urlopen('https://api.pwnedpasswords.com/range/{0}'.format(password_sha1_prefix))
    data = str(response.read())

    if response.code not in [200]:
        raise ValueError(data)

    return [str(passwd) for passwd in data.split('\\r\\n')]


def password_has_been_pwned(password):
    """
    Chacks if the provided password has been pwned by querying the haveibeenpwned API

    :param password:
    :type: str
    :return: bool
    """
    password_sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

    password_sha1_prefix = password_sha1[:5]

    pwned_password_suffixes = get_pwned_password_range(password_sha1_prefix)

    full_pwned_passwords_sha1 = [password_sha1_prefix + suffix[:35] for suffix in pwned_password_suffixes]

    return password_sha1 in full_pwned_passwords_sha1


def is_strong(password, min_length=MIN_PASSWORD_LENGTH):
    """
    Determines whether the password is strong enough using the following criteria:
    - it does not contain spaces
    - its length is equal or bigger that max_length
    - it has been pwned before (checked via haveibeenpwned API)

    :param password:
    :type: str
    :param min_length:
    :type: int
    :return: bool
    """
    return ' ' not in password \
        and len(password) >= min_length \
        and not password_has_been_pwned(password)


def is_empty(string):
    """
    Determines whether the provided string is empty or None or consists of only empty spaces
    :param string:
    :type str:
    :return: bool
    """
    return string is None or len(string) == 0 or not bool(string.replace(' ', ''))


class User:

    def __init__(self, user_id, description, username=None, password=None):
        """
        :param user_id:
        :type: str
        :param description:
        :type: str
        :param username:
        :type: str or None
        :param password:
        :type: str or None
        """
        self.id = user_id
        self.description = description
        self.username = username
        self.password = password


def prompt_for_user(user):
    """
    Updates the username and password of the provided user by prompting from them
    :param user:
    :type: User
    :return: User
    """
    input_method = _get_input_method()

    user.username = input_method(" username: ".format(user.username))
    while is_empty(user.username):
        sys.stdout.write('The username should not be empty.\n')
        user.username = input_method(" username: ".format(user.username))
    user.password = getpass(prompt=" password: ")

    while not is_strong(user.password):
        sys.stdout.write('The password is not strong enough. Please try again.\n')
        user.password = getpass(prompt=" password: ")

    return user


def autofill_user(user):
    """
    Updates the username and password of the provided user by assigning the lowercase user_id as username and generating
    a random password.
    :param user:
    :type=: User
    :return:
    """
    user.username = user.id.lower()
    user.password = uuid.uuid4().hex

    return user


def make_user(user_id, description, with_prompt=True):
    """

    :param user_id:
    :type: str
    :param description:
    :type: str
    :param with_prompt:
    :type: bool
    :return: User
    """
    user = User(user_id=user_id, description=description)

    sys.stdout.write("{0}\n".format(description))

    if with_prompt:
        user = prompt_for_user(user)
    else:
        user = autofill_user(user)

    sys.stdout.write("[OK]\n\n")

    return user


def load_config(config_file):
    """
    Parses the providing JSON file
    :param config_file:
    :type: str
    :return: dict
    """
    with open(config_file, 'r') as f:
        try:
            config = json.loads(f.read())
        except Exception as e:
            sys.stdout.write("Error while loading config file: {0}\n".format(str(e)))
            exit(0)

    return config


def save_users(users, output_file):
    """
    :param users:
    :type: list of User
    :param output_file:
    :type: str
    """
    with open(output_file, 'w') as f:
        for u in users:
            f.write('{0}_USER={1}\n'.format(u.id, u.username))
            f.write('{0}_PASS={1}\n'.format(u.id, u.password))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_file', required=True,
                        help="The file containing the user data")
    parser.add_argument('-o', '--output_file', required=True,
                        help="The file where usernames and passwords will be saved")
    parser.add_argument('-p', '--prompt', action='store_true',
                        help="Prompts for username and password")
    args = parser.parse_args()

    if not os.path.exists(args.config_file):
        sys.stdout.write("Invalid config_file\n")
        exit(1)

    sys.stdout.write("\n")

    config = load_config(args.config_file)

    users = [
        make_user(user_id, description, with_prompt=args.prompt)
        for user_id, description in config['USERS'].items()
    ]

    save_users(users, args.output_file)
