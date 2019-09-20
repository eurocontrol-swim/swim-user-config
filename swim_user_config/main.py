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
import json
import sys
from getpass import getpass

from swim_user_config import pwned_passwords

__author__ = "EUROCONTROL (SWIM)"

MIN_LENGTH = 5

USERS = [
    'DB',
    'SM_ADMIN',
    'SWIM_ADSB',
    'SWIM_EXPLORER',
]


def is_strong(password: str) -> bool:
    """
    Performs conformance checks on the provided password:
        1. it should not be less that MIN_LENGTH
        2. it should not be among the pwned passwords that can be found in haveibeenpwned
    :param password:
    :return:
    """
    return len(password) >= MIN_LENGTH and not pwned_passwords.password_has_been_pwned(password)


def main():
    if not len(sys.argv) == 2:
        print('Output file not provided')
        return

    output_file = sys.argv[1]

    print('SWIM User Configuration')
    print('-----------------------\n')

    user_config = {}

    for user in USERS:
        username = input(f"{user} (username): ")
        while True:
            password = getpass(prompt=f"{user} (password): ")
            if is_strong(password):
                break

            print('The password is not strong enough. Please try again:')

        user_config[user] = [username, password]

    with open(output_file, 'w') as f:
        f.write(json.dumps(user_config))


if __name__ == '__main__':
    main()
