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
from unittest import mock

import pytest
import requests

from swim_user_config.pwned_passwords import get_pwned_password_range, password_has_been_pwned

__author__ = "EUROCONTROL (SWIM)"


@pytest.mark.parametrize('pwnedpasswords_response, expected_password_list', [
    (
        'hash1\r\nhash2\r\nhash3\r\nhash4\r\nhash5\r\nhash6\r\nhash7\r\nhash8\r\nhash9',
        ['hash1', 'hash2', 'hash3', 'hash4', 'hash5', 'hash6', 'hash7', 'hash8', 'hash9']
    )
])
def test_get_pwned_password_range(pwnedpasswords_response, expected_password_list):
    with mock.patch.object(requests.Session, 'get') as mock_get:
        response = mock.Mock()
        response.text = pwnedpasswords_response
        response.status_code = 200

        mock_get.return_value = response

        assert expected_password_list == get_pwned_password_range('hash1')


def test_get_pwned_password_range__response_status_code_not_200__raises_valueerror():
    with mock.patch.object(requests.Session, 'get') as mock_get:
        response = mock.Mock()
        response.text = 'error text'
        response.status_code = 400

        mock_get.return_value = response

        with pytest.raises(ValueError) as e:
            get_pwned_password_range('hash1')

        assert 'error text' == str(e.value)


def test_password_has_been_pwned():
    with mock.patch('swim_user_config.pwned_passwords.get_pwned_password_range') as mock_range:
        pwned_password = 'password'

        mock_range.return_value = [hashlib.sha1(pwned_password.encode('utf-8')).hexdigest().upper()[5:] + ':1']

        assert password_has_been_pwned(pwned_password) is True

