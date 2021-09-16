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
import base64
import kubernetes
from kubernetes.client import V1Secret
from kubernetes.client import V1ObjectMeta
import typing

from secrets.driver import _SecretDriver
from secrets.common import Secret, SecretOptions


class KubernetesSecretsDriver(_SecretDriver):
    """

    """
    def __init__(self, namespace: str):
        """
        Initializes the KubernetesSecretsDriver
        """
        kubernetes.config.load_incluster_config()
        self.namespace = namespace
        kcl = kubernetes.client.ApiClient()
        self.core_api = kubernetes.client.CoreV1Api(kcl)

    @classmethod
    def _encode_secret_data(cls, secret):
        """
        Encodes the secret data into a dictionary appropriate for k8s
        """
        # Need to base64 encode the secrets before sending to k8s
        data = {}
        for key, value in secret.data.items():
            encoded_value = base64.b64encode(bytes(value)).decode('utf-8')
            data[key] = encoded_value

    def create(self, secret: Secret, options: SecretOptions = None):
        """
        Creates a new secret in the secret Kubernetes Secret Service.
        """
        try:
            resp = self.core_api.create_namespaced_secret(
                namespace=self.namespace,
                body=V1Secret(
                    api_version="v1",
                    metadata=V1ObjectMeta(name=secret.name,
                                          namespace=self.namespace),
                    # TODO(wolsen) labels?,
                    type='Opaque',
                    data=self._encode_secret_data(secret),
                ),
            )
            secret.uuid = resp.metadata.uid
            return secret
        except kubernetes.client.rest.ApiException as e:
            # TODO(wolsen) proper exceptions
            raise

    def delete(self, secret: Secret):
        """

        """
        try:
            self.core_api.delete_namespaced_secret(name=secret.name,
                                                   namespace=self.namespace)
        except kubernetes.client.rest.ApiException as e:
            # TODO(wolsen) proper exceptions
            raise

    def update(self, secret: Secret, options: SecretOptions = None):
        """

        """
        try:
            self.core_api.patch_namespaced_secret(
                name=secret.name, namespace=self.namespace,
                body=V1Secret(
                    api_version="v1",
                    metadata=V1ObjectMeta(name=secret.name,
                                          namespace=self.namespace),
                    type='Opaque',
                    data=self._encode_secret_data(secret),
                ),
            )
            return secret
        except kubernetes.client.rest.ApiException as e:
            # TODO(wolsen) proper exceptions
            raise

    def get_secret(self, secret: typing.Union[Secret, str]) -> Secret:
        """
        Returns the requested secret.
        """
        try:
            name = secret
            if isinstance(secret, Secret):
                name = secret.name

            v1secret = self.core_api.read_namespaced_secret(
                name=name, namespace=self.namespace
            )
            data = v1secret.data
            if not data:
                # TODO(wolsen) raise an exception?
                return None

            metadata = v1secret.metadata

            # TODO(wolsen) feels a bit strict - can probably just create a
            #  general secret, but revisit this. TLS Secrets can be Opaque or
            #  specified, but in the end it will just be a dict of data.
            secret_type = metadata['type']
            if secret_type != 'Opaque':
                raise ValueError(f'Unsupported secret type {secret_type}')

            return Secret(name=metadata.name, uuid=metadata.uid,
                          value=data)
        except kubernetes.client.rest.ApiException as e:
            # May indicate that the secret doesn't exist or that we're
            # unauthorized to access the secret. Either way, let's not return
            # anything
            # TODO(wolsen) proper exceptions - can use ApiException.status for
            #  the status code. Seems we can get 401 (unauthorized) and 404
            #  (not found).
            raise
