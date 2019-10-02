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
import sys
from dataclasses import dataclass
from getpass import getpass
from typing import Dict, Union, Any

import yaml
from pkg_resources import resource_filename
from swim_backend.auth.passwords import is_strong

__author__ = "EUROCONTROL (SWIM)"

MIN_LENGTH = 10


@dataclass
class User:
    id: str
    description: str
    username: str
    password: Union[str, None]


def _load_config(filename: str) -> Union[Dict[str, Any], None]:
    """

    :param filename:
    :return:
    """
    with open(filename) as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)

    return obj or None


def _prompt_for_user(user: User) -> User:
    """

    :param user:
    :return:
    """
    print(f'\n{user.description}')
    user.username = input(f" username [{user.username}]: ") or user.username
    user.password = getpass(prompt=f" password: ")

    while not is_strong(user.password, MIN_LENGTH):
        print('The password is not strong enough. Please try again:')
        user.password = getpass(prompt=f" password: ")

    return user


def main():

    output_file = sys.argv[1] if len(sys.argv) == 2 else '.env'

    config = _load_config(resource_filename(__name__, 'config.yml'))

    if config is None:
        print("Error while loading config file")
        exit(0)

    users = [User(id=user_id,
                  description=data.get('description'),
                  username=data.get('default_user'),
                  password=None)
             for user_id, data in config['USERS'].items()]

    users = [_prompt_for_user(user) for user in users]

    with open(output_file, 'w') as f:
        for user in users:
            f.write(f'{user.id}_USER={user.username}\n')
            f.write(f'{user.id}_PASS={user.password}\n')


if __name__ == '__main__':
    main()
