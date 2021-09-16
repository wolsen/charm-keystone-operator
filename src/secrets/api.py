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

from ops.charm import CharmBase
from secrets.common import Secret, SecretOptions
from secrets.driver import _SecretDriver


class Secrets:

    def __init__(self, charm: CharmBase, driver: _SecretDriver = None):
        """Creates a new Secrets manager for the specified charm.

        :param meta: the metadata for the charm
        :type meta: CharmMeta
        :param driver: the storage backend to use for secrets
        :type driver: the implementation class for accessing secrets
        """
        # If the driver is provided, then use the provided driver.
        if driver is not None:
            self._driver = driver
        elif charm.meta.containers:
            # If there are containers defined in charm metadata, then it means
            # the charm is running within Kubernetes so use the Kubernetes
            # backend.
            from secrets.kubernetes import KubernetesSecretsDriver
            self._driver = KubernetesSecretsDriver(namespace=charm.model.name)
        else:
            raise NotImplementedError('Backend for non-k8s charms not yet '
                                      'implemented')

    def create(self, secret: Secret, options: SecretOptions = None):
        """
        Creates the specified secret.

        :param secret: the secret to create
        :type secret: Secret
        :param options: the options to create for the secret
        :type options: SecretOptions
        :raises: SecretError if there is an error creating the secret
        """
        return self._driver.create(secret, options)

    def delete(self, secret: Secret):
        """
        Deletes the specified secret
        """
        return self._driver.delete(secret)

    def update(self, secret: Secret, options: SecretOptions = None):
        """
        Updates the specified secret.

        """
        return self._driver.update(secret, options)

    def get_secret(self, secret: typing.Union[Secret, str]) -> Secret:
        """

        """
        return self._driver.get_secret(secret)

    def get_data(self, secret: typing.Union[Secret, str])\
            -> typing.Union[str, dict, None]:
        """
        Returns the secret value

        """
        secret = self.get_secret(secret)
        if secret is None:
            return None
        return secret.get_data()

    def grant(self, secret: typing.Union[Secret, str], scope: str) -> None:
        """

        """
        self._driver.grant(secret, scope)

    def revoke(self, secret: typing.Union[Secret, str], scope: str) -> None:
        """

        """
        self._driver.revoke(secret, scope)
