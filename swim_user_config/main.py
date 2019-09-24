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
from collections import namedtuple
from getpass import getpass
from typing import Dict, Union, List

import yaml
from pkg_resources import resource_filename

from swim_user_config import pwned_passwords

__author__ = "EUROCONTROL (SWIM)"

MIN_LENGTH = 10

User = namedtuple('User', 'id, username, password')


def _is_strong(password: str) -> bool:
    """
    Performs conformance checks on the provided password:
        1. it should not be less that MIN_LENGTH
        2. it should not be among the pwned passwords that can be found in haveibeenpwned
    :param password:
    :return:
    """
    return len(password) >= MIN_LENGTH \
        and not pwned_passwords.password_has_been_pwned(password)


def _load_config(filename: str) -> Union[Dict[str, Dict[str, List[str]]], None]:
    """

    :param filename:
    :return:
    """
    with open(filename) as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)

    return obj or None


def _dump_user(user: User, path: str) -> None:
    """

    :param user:
    :param path:
    """
    with open(path, 'a') as f:
        f.write(f'\n{user.id}_USERNAME={user.username}\n')
        f.write(f'\n{user.id}_PASSWORD={user.password}\n')


def _prompt_for_user(user_id: str) -> User:
    """

    :param user_id:
    :return:
    """
    username = input(f"{user_id} (username): ")
    password = getpass(prompt=f"{user_id} (password): ")

    while not _is_strong(password):
        print('The password is not strong enough. Please try again:')
        password = getpass(prompt=f"{user_id} (password): ")

    return User(id=user_id, username=username, password=password)


def main():

    config = _load_config(resource_filename(__name__, 'config.yml'))

    if config is None:
        print("Error while loading config file")
        exit(0)

    users = [_prompt_for_user(user_id) for user_id in config['ENV_FILE_PATHS_PER_USER'].keys()]

    for user in users:
        for path in config['ENV_FILE_PATHS_PER_USER'][user.id]:
            try:
                _dump_user(user, path)
            except OSError as e:
                print(f"Error while saving user {user.id} in {path}: {str(e)}. Skipping...")
                continue


if __name__ == '__main__':
    main()
