#!/usr/bin/env python3
# Copyright 2021 Billy Olsen
# See LICENSE file for licensing details.

import json
import logging
import typing

from ops.framework import EventBase
from ops.framework import EventSource
from ops.framework import Object
from ops.framework import ObjectEvents
from ops.framework import StoredState


class PeersRelationCreatedEvent(EventBase):
    """
    The PeersRelationCreatedEvent indicates that the peer relation now exists.
    It does not indicate that any peers are available or have joined, simply
    that the relation exists. This is useful to to indicate that the
    application databag is available for storing information shared across
    units.
    """
    pass


class CharmPasswordChangedEvent(EventBase):
    """
    The CharmPasswordChangedEvent indicates that the leader unit has changed
    the password that the charm administrator uses.
    """
    pass


class BootstrapEvent(EventBase):
    """
    The BootstrapEvent indicates that the leader has bootstrapped the
    service.
    """
    pass


class KeystoneOperatorPeersEvents(ObjectEvents):
    peers_relation_created = EventSource(PeersRelationCreatedEvent)
    charm_password_changed = EventSource(CharmPasswordChangedEvent)
    bootstrapped = EventSource(BootstrapEvent)


class KeystoneOperatorPeers(Object):

    on = KeystoneOperatorPeersEvents()
    state = StoredState()
    CHARM_PASSWORD = "keystone_password"
    BOOTSTRAPPED = "keystone_bootstrapped"
    DEFAULT_DOMAIN_ID = "default_domain_id"
    ADMIN_DOMAIN_ID = "admin_domain_id"
    ADMIN_PROJECT_ID = "admin_project_id"
    ADMIN_USER = "admin_user"
    SERVICE_DOMAIN_ID = "service_domain_id"
    SERVICE_PROJECT_ID = "service_project_id"

    def __init__(self, charm, relation_name):
        super().__init__(charm, relation_name)
        self.relation_name = relation_name
        self.framework.observe(
            charm.on[relation_name].relation_created,
            self.on_created
        )
        self.framework.observe(
            charm.on[relation_name].relation_joined,
            self.on_joined
        )
        self.framework.observe(
            charm.on[relation_name].relation_changed,
            self.on_changed
        )

    @property
    def peers_rel(self):
        return self.framework.model.get_relation(self.relation_name)

    @property
    def _app_data_bag(self) -> typing.Dict[str, str]:
        """

        """
        return self.peers_rel.data[self.peers_rel.app]

    def on_created(self, event):
        logging.info('KeystonePeers on_created')
        self.on.peers_relation_created.emit()

    def on_joined(self, event):
        logging.info('KeystonePeers on_joined')
        self.on.charm_password_changed.emit()

    def on_changed(self, event):
        logging.info('KeystonePeers on_changed')
        self.on.bootstrapped.emit()

    def set_charm_password(self, password) -> None:
        """

        """
        logging.info('Setting charm password')
        self.peers_rel.data[self.peers_rel.app][self.CHARM_PASSWORD] = password
        self.on.charm_password_changed.emit()

    def set_bootstrapped(self, bootstrapped: bool, default_domain_id: str,
                         admin_domain_id: str, admin_project_id: str,
                         admin_user: str, service_domain_id: str,
                         service_project_id: str) -> None:
        """

        """
        relation_data = self.peers_rel.data[self.peers_rel.app]
        if bootstrapped:
            logging.info('Setting shared project information')
            relation_data[self.BOOTSTRAPPED] = json.dumps(bootstrapped)
            relation_data[self.DEFAULT_DOMAIN_ID] = default_domain_id
            relation_data[self.ADMIN_DOMAIN_ID] = admin_domain_id
            relation_data[self.ADMIN_PROJECT_ID] = admin_project_id
            relation_data[self.ADMIN_USER] = admin_user
            relation_data[self.SERVICE_DOMAIN_ID] = service_domain_id
            relation_data[self.SERVICE_PROJECT_ID] = service_project_id
        else:
            logging.info('Clearing shared project information')
            relation_data[self.BOOTSTRAPPED] = json.dumps(bootstrapped)
            relation_data[self.DEFAULT_DOMAIN_ID] = None
            relation_data[self.ADMIN_DOMAIN_ID] = None
            relation_data[self.ADMIN_PROJECT_ID] = None
            relation_data[self.ADMIN_USER] = None
            relation_data[self.SERVICE_DOMAIN_ID] = None
            relation_data[self.SERVICE_PROJECT_ID] = None

    @property
    def charm_password(self) -> typing.Union[str, None]:
        if not self.peers_rel:
            return None
        return self.peers_rel.data[self.peers_rel.app].get(self.CHARM_PASSWORD)

    @property
    def is_bootstrapped(self) -> bool:
        """
        Indicates whether or not the leader unit has bootstrapped the keystone
        service. Returns True when the relation data indicates that the leader
        has completed the bootstrap sequence, False otherwise.
        """
        # If there is peer relationship yet, then this is early in the charm
        # initialization sequence so report False
        if not self.peers_rel:
            return False

        relation_data = self.peers_rel.data[self.peers_rel.app]
        bs = relation_data.get(self.BOOTSTRAPPED)

        # If for some reason its empty string or None, return False
        if not bs:
            return False

        # NOTE(wolsen) this can raise a JSONDecodeError, however it indicates
        #  that something has gone horribly wrong so this error is not being
        #  caught intentionally
        return json.loads(bs)

    @property
    def default_domain_id(self) -> typing.Union[str, None]:
        return self._app_data_bag.get(self.DEFAULT_DOMAIN_ID)

    @property
    def admin_domain_id(self) -> typing.Union[str, None]:
        return self._app_data_bag.get(self.ADMIN_DOMAIN_ID)

    @property
    def admin_project_id(self) -> typing.Union[str, None]:
        return self._app_data_bag.get(self.ADMIN_PROJECT_ID)

    @property
    def admin_user(self) -> typing.Union[str, None]:
        return self._app_data_bag.get(self.ADMIN_USER)

    @property
    def service_domain_id(self) -> typing.Union[str, None]:
        return self._app_data_bag.get(self.SERVICE_DOMAIN_ID)

    @property
    def service_project_id(self) -> typing.Union[str, None]:
        return self._app_data_bag.get(self.SERVICE_PROJECT_ID)
