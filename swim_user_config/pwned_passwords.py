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
import hashlib
from typing import List

from requests import Session

__author__ = "EUROCONTROL (SWIM)"


def get_pwned_password_range(password_sha1_prefix: str) -> List[str]:
    """
    Retrieves a range of sha1 pwned passwords from haveibeenpwned API whose 5 first characters match with the provided
    sha1 prefix.

    :param password_sha1_prefix: must be 5 characters long
    :return:
    """
    session = Session()

    response = session.get(f'https://api.pwnedpasswords.com/range/{password_sha1_prefix}')

    if response.status_code not in [200]:
        raise ValueError(response.text)

    return response.text.split('\r\n')


def password_has_been_pwned(password: str) -> bool:
    """
    Chacks if the provided password has been pwned by querying the haveibeenpwned API

    :param password:
    :return:
    """
    password_sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

    password_sha1_prefix = password_sha1[:5]

    pwned_password_suffixes = get_pwned_password_range(password_sha1_prefix)

    full_pwned_passwords_sha1 = [password_sha1_prefix + suffix[:35] for suffix in pwned_password_suffixes]

    return password_sha1 in full_pwned_passwords_sha1
