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

from secrets.common import Secret, SecretOptions


class _SecretDriver:
    """

    """
    def create(self, secret: Secret, options: SecretOptions = None):
        pass

    def delete(self, secret: Secret):
        pass

    def update(self, secret: Secret, options: SecretOptions = None):
        pass

    def get_secret(self, secret: typing.Union[Secret, str]) -> Secret:
        pass

    def grant(self, secret: typing.Union[Secret, str], scope: str) -> None:
        pass

    def revoke(self, secret: typing.Union[Secret, str], scope: str) -> None:
        pass

