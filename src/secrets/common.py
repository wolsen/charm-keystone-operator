# Copyright 2021, Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import typing


class SecretError(Exception):
    pass


class SecretOptions:
    """

    """
    pass


class Secret:
    """
    The Secret class represents a base secret within the system.

    A Secret represents some arbitrary data that needs to be stored securely
    and should be treated as sensitive data. This can include passwords, TLS
    certificates, access keys, etc.

    A Secret consists of a user friendly name, a unique ID, and the sensitive
    content. The sensitive content may consist of simple data such as a string
    or more complex data such as a dictionary with multiple key/value pairs.

    The unique ID of a secret should be treated as read-only and is provided
    by the secret storage implementation. It is not intended to be manipulated
    by other code. Doing so may have strange side effects.
    """
    def __init__(self, name: str, uuid: str = None, data: dict = None,
                 **kwargs):
        """
        Creates a new Secret that stores secret data.

        """
        self.name = name
        self.uuid = uuid
        if data is not None:
            self.data = data
        elif kwargs:
            self.data = {}
            self.data.update(kwargs)
        else:
            self.data = None

    def get_data(self) -> typing.Union[dict, None]:
        """
        Returns the secret data
        """
        return self.data


class Password(Secret):
    """
    A Secret containing a password
    """
    def __init__(self, name: str, uuid: str, password: str):
        """

        """
        super(Password, self).__init__(name, uuid, password=password)


class TLS(Secret):
    """
    TLS Secrets for storing certificates
    """
    def __init__(self, name: str, uuid: str, cert: str, key: str = None):
        """

        """
        super(TLS, self).__init__(name, uuid, cert=cert, key=key)
        self._cert = cert
        self._key = key

    def certificate(self) -> str:
        """

        """
        return self._cert

    def key(self) -> str:
        """

        """
        return self._key
