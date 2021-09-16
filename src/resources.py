#
# Copyright 2021 Canonical
#

import logging
import typing

from kubernetes import kubernetes

logger = logging.getLogger(__name__)


class KeystoneResources:
    """
    Handles the creation, deletion and management of Kubernetes resources
    required by the Keystone charm, but are not currently available via Juju.
    """

    def __init__(self, charm):
        self.model = charm.model
        self.app = charm.app
        self.config = charm.config
        self.namespace = charm.namespace

        kcl = kubernetes.client.ApiClient()
        self.apps_api = kubernetes.client.AppsV1Api(kcl)
        self.core_api = kubernetes.client.CoreV1Api(kcl)
        self.auth_api = kubernetes.client.RbacAuthorizationV1Api(kcl)

    def apply(self) -> None:
        """
        Create the required Kubernetes resources for Keystone.

        The required resources for keystone include the following:
          - Fernet Repository Secrets (Opaque Secret)
          - Credential Repository Secrets (Opaque Secret)
          - Admin Credentials (Opaque Secret)
          - TLS Certificates (TLS Secret)
        """
        for sa in self._service_accounts:
            svc_accounts = self.core_api.list_namespaced_service_account(
                namespace=sa["namespace"],
                field_selector=f"metadata.name={sa['body'].metadata.name}",
            )
            if not svc_accounts.items:
                self.core_api.create_namespaced_service_account(**sa)
            else:
                logger.info("service account '%s' in namespace '%s' exists,"
                            "patching", sa["body"].metadata.name,
                            sa["namespace"])
                self.core_api.patch_namespaced_service_account(
                    name=sa["body"].metadata.name, **sa
                )

        # Create kubernetes secrets
        for secret in self._secrets:
            s = self.core_api.list_namespaced_secret(
                namespace=secret["namespace"],
                field_selector=f"metadata.name={secret['body'].metadata.name}",
            )
            if not s.items:
                self.core_api.create_namespaced_secret(**secret)
            else:
                logger.info("secret '%s' in namespace '%s' exists, not "
                            "creating", secret["body"].metadata.name,
                            secret["namespace"])

    @property
    def _service_accounts(self) -> list:
        """Return a dictionary containing parameters for the keystone service
        account.
        """
        return [
            {
                "namespace": self.namespace,
                "body": kubernetes.client.V1ServiceAccount(
                    api_version="v1",
                    metadata=kubernetes.client.V1ObjectMeta(
                        namespace=self.namespace,
                        name="keystone",
                        labels={"app.kubernetes.io/name": self.app.name},
                    ),
                ),
            }
        ]

    @property
    def _secrets(self) -> list:
        """
        Return a list of secrets used by the Keystone service. This includes
        the following:

          * Admin Credentials
          * Fernet Repository Secrets
          * Credential Repository Secrets
          * TLS Certificates (TLS Secret)
        """
        return [
            self._secret_def("admin-credentials"),
            self._secret_def("fernet-keys"),
            self._secret_def("credential-keys"),
            # TODO(wolsen) enable when certs are ready
            # self._secret_def("tls-certs", secret_type="kubernetes.io/tls"),
        ]

    def _secret_def(self, name: str, secret_type: str = "Opaque",
                data: typing.Union[dict, None] = None) -> dict:
        """
        Returns a secret definition
        """
        return {
            "namespace": self.namespace,
            "body": kubernetes.client.V1Secret(
                api_version="v1",
                metadata=kubernetes.client.V1ObjectMeta(
                    namespace=self.namespace,
                    name=name,
                    labels={"app.kubernetes.io/name": self.app.name},
                ),
                type=secret_type,
                data=data,
            ),
        }

    @property
    def _services(self) -> list:
        """
        Returns a list of service definitions.
        """
        return [
            {
                "namespace": self.namespace,
                "body": kubernetes.client.V1Service(
                    api_version="v1",
                    metadata=kubernetes.client.V1ObjectMeta(
                        namespace=self.namespace,
                        name=self.app.name,
                        labels={"app.kubernetes.io/name": self.app.name},
                    ),
                    spec=kubernetes.client.V1ServiceSpec(
                        ports=[
                            kubernetes.client.V1ServicePort(
                                name="keystone-public",
                                port=self.config['service-port'],
                                target_port=self.config['service-port'],
                            )
                        ],
                        selector={"app.kubernetes.io/name": self.app.name},
                    ),
                ),
            },
        ]
