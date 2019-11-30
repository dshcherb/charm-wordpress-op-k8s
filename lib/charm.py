#!/usr/bin/env python3

from op.charm import CharmBase, CharmEvents, RelationUnitEvent
from op.framework import (
    Event,
    EventBase,
    StoredState,
)

from op.main import main

import subprocess
import yaml


class WordPressReadyEvent(EventBase):
    pass


class WordPressCharmEvents(CharmEvents):
    wordpress_ready = Event(WordPressReadyEvent)


class Charm(CharmBase):

    on = WordPressCharmEvents()

    state = StoredState()

    def __init__(self, *args):
        super().__init__(*args)

        self.framework.observe(self.on.install, self)
        self.framework.observe(self.on.start, self)
        self.framework.observe(self.on.stop, self)
        self.framework.observe(self.on.config_changed, self)

        self.framework.observe(self.on.db_relation_changed, self)

        self.framework.observe(self.on.wordpress_ready, self)

    def on_install(self, event):
        # Initialize Charm state here
        log('Ran on_install')

    def on_start(self, event):
        log('Ran start')

    def on_stop(self, event):
        log('Ran stop')

    def on_config_changed(self, event):
        log('Ran on_config_changed')

        try:
            applied_spec = self.state.spec
        except AttributeError:
            applied_spec = None

        new_spec = self.make_pod_spec()

        if applied_spec != new_spec:
            self.framework.model.pod.set_spec(new_spec)
            self.state.spec = new_spec

    def on_wordpress_ready(self, event):
        pass

    def on_db_relation_changed(self, event):
        if not self.state.ready:
            event.defer()
            return

        if isinstance(event, RelationUnitEvent):
            # event.relation.data[event.unit].get('hostname')
            # event.relation.data[event.unit].get('port')
            # event.relation.data[event.unit].get('password')
            pass

    def make_pod_spec(self):
        config = self.framework.model.config

        container_config = self.sanitized_container_config()
        if container_config is None:
            return  # status already set

        ports = [{"name": "http", "containerPort": 80, "protocol": "TCP"}]

        spec = {
            "containers": [
                {"name": self.framework.model.app.name, "image": config["image"], "ports": ports, "config": container_config}
            ]
        }

        # Add the secrets after logging
        config_with_secrets = self.full_container_config()
        if config_with_secrets is None:
            return None

        container_config.update(config_with_secrets)

        return spec

    def sanitized_container_config(self):
        """Uninterpolated container config without secrets"""
        config = self.framework.model.config

        if config["container_config"].strip() == "":
            container_config = {}
        else:
            container_config = yaml.safe_load(self.framework.model.config["container_config"])
            if not isinstance(container_config, dict):
                status_set('blocked', "container_config is not a YAML mapping")
                return None
        # container_config["WORDPRESS_DB_HOST"] = config["db_host"]
        # container_config["WORDPRESS_DB_USER"] = config["db_user"]
        return container_config

    def full_container_config(self):
        """Uninterpolated container config with secrets"""
        config = self.framework.model.config
        container_config = self.sanitized_container_config()
        if container_config is None:
            return None
        if config["container_secrets"].strip() == "":
            container_secrets = {}
        else:
            container_secrets = yaml.safe_load(config["container_secrets"])
            if not isinstance(container_secrets, dict):
                status_set('blocked', "container_secrets is not a YAML mapping")
                return None
        container_config.update(container_secrets)
        # container_config["WORDPRESS_DB_PASSWORD"] = config["db_password"]
        return container_config

def status_set(workload_state, message):
    """Set the workload state with a message

    Use status-set to set the workload state with a message which is visible
    to the user via juju status.

    workload_state -- valid juju workload state.
    message        -- status update message
    """
    valid_states = ['maintenance', 'blocked', 'waiting', 'active']

    if workload_state not in valid_states:
        raise ValueError(
            '{!r} is not a valid workload state'.format(workload_state)
        )

    subprocess.check_call(['status-set', workload_state, message])

def log(message, level=None):
    """Write a message to the juju log"""
    command = ['juju-log']
    if level:
        command += ['-l', level]
    if not isinstance(message, str):
        message = repr(message)

    # https://elixir.bootlin.com/linux/latest/source/include/uapi/linux/binfmts.h
    # PAGE_SIZE * 32 = 4096 * 32
    MAX_ARG_STRLEN = 131072
    command += [message[:MAX_ARG_STRLEN]]
    # Missing juju-log should not cause failures in unit tests
    # Send log output to stderr
    subprocess.call(command)


if __name__ == '__main__':
    main(Charm)
