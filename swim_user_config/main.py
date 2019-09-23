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
from getpass import getpass
from typing import Any, Dict, Union, List, Type, Tuple

import yaml
from pkg_resources import resource_filename

from swim_user_config import pwned_passwords


__author__ = "EUROCONTROL (SWIM)"

ConfigType = Dict[str, Dict[str, List[str]]]

MIN_LENGTH = 5

USERS = [
    'DB',
    'SM_ADMIN',
    'SWIM_ADSB',
    'SWIM_EXPLORER',
]


def _is_strong(password: str) -> bool:
    """
    Performs conformance checks on the provided password:
        1. it should not be less that MIN_LENGTH
        2. it should not be among the pwned passwords that can be found in haveibeenpwned
    :param password:
    :return:
    """
    return len(password) >= MIN_LENGTH and not pwned_passwords.password_has_been_pwned(password)


def _load_config(filename: str) -> Union[ConfigType, None]:
    """

    :param filename:
    :return:
    """
    with open(filename) as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)

    return obj or None


def _dump_credentials(user_prefix: str, username: str, password: str, path: str) -> None:
    """

    :param user_prefix:
    :param username:
    :param password:
    :param path:
    """
    with open(path, 'a') as f:
        f.write(f'export {user_prefix}_USERNAME={username}\n')
        f.write(f'export {user_prefix}_PASSWORD={password}\n')


def _get_user_credentials(user_prefix: str) -> Tuple[str, str]:
    """

    :param user_prefix:
    :return:
    """
    username = input(f"{user_prefix} (username): ")
    password = getpass(prompt=f"{user_prefix} (password): ")

    while not _is_strong(password):
        print('The password is not strong enough. Please try again:')
        password = getpass(prompt=f"{user_prefix} (password): ")

    return username, password


def _get_all_credentials(user_prefixes: List[str]) -> Dict[str, Tuple[str, str]]:
    """

    :param user_paths:
    :return:
    """
    result = {user_prefix: _get_user_credentials(user_prefix) for user_prefix in user_prefixes}

    return result


def main():
    app_config = _load_config(resource_filename(__name__, 'config.yml'))

    if app_config is None:
        print("Error while loading config file")
        exit(0)

    user_paths = app_config['USER_ENV_FILE_PATHS']

    all_credentials = _get_all_credentials(list(user_paths.keys()))

    for user_prefix, (username, password) in all_credentials.items():
        for path in user_paths[user_prefix]:
            _dump_credentials(user_prefix, username, password, path)


if __name__ == '__main__':
    main()
