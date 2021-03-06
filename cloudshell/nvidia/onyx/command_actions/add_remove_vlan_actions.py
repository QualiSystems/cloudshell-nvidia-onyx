#!/usr/bin/python

import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

from cloudshell.nvidia.onyx.command_templates import add_remove_vlan, iface


class AddRemoveVlanActions:
    CREATE_VLAN_VALIDATION_PATTERN = re.compile(
        r"[Ii]nvalid\s*([Ii]nput|[Cc]ommand)|[Cc]ommand rejected", re.IGNORECASE
    )
    CHECK_VLAN_MODE_NOT_REJECTED = re.compile(
        r"^command\s*rejected.*encapsulation\s*is\s*\S*Auto", re.IGNORECASE
    )
    CREATE_VLAN_ERROR_PATTERN = re.compile(r"%.*\\.", re.IGNORECASE)
    CHECK_ANY_VLAN_CFGED = re.compile(
        r"switchport.*vlan\s+\d+$|switchport\s+mode\s+trunk",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )

    def __init__(self, cli_service, logger):
        """Add remove vlan.

        :param cli_service: config mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    @staticmethod
    def verify_interface_configured(current_config):
        """Verify interface configuration.

        :param current_config:
        :return: True or False
        """
        return bool(AddRemoveVlanActions.CHECK_ANY_VLAN_CFGED.search(current_config))

    @staticmethod
    def verify_interface_has_vlan_assigned(vlan_range, current_config):
        """Verify interface configuration.

        :param vlan_range:
        :param current_config:
        :return: True or False
        """
        success = True
        lines = current_config.splitlines()
        for vlans in vlan_range.split(","):
            if all(line for line in lines if not line.endswith(vlans)):
                success = False
        return success

    @staticmethod
    def verify_interface_has_no_vlan_assigned(current_config):
        """Verify interface configuration.

        :param vlan_range:
        :param current_config:
        :return: True or False
        """
        success = True

        if not re.search(
            r"switchport.*vlan.*",
            current_config,
            re.IGNORECASE,
        ):
            success = False
        return success

    def create_vlan(self, vlan_range, action_map=None, error_map=None):
        """Create vlan entity on the device.

        :param vlan_range: range of vlans to be created
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        for vlans in vlan_range.split(","):
            result = CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.CONFIGURE_VLAN,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(vlan_id=vlans)
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.EXIT,
                action_map=action_map,
                error_map=error_map,
            ).execute_command()
            if self.CREATE_VLAN_VALIDATION_PATTERN.search(result):
                self._logger.info("Unable to create vlan, proceeding")

    def set_vlan_to_interface(
        self,
        vlan_range,
        port_mode,
        port_name,
        qnq,
        action_map=None,
        error_map=None,
    ):
        """Assign vlan to a certain interface.

        :param vlan_range: range of vlans to be assigned
        :param port_mode: switchport mode
        :param port_name: interface name
        :param qnq: qinq settings (dot1q tunnel)
        :param c_tag: selective qnq
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        CommandTemplateExecutor(
            self._cli_service, iface.CONFIGURE_INTERFACE
        ).execute_command(port_name=port_name)

        CommandTemplateExecutor(
            self._cli_service,
            iface.NO_SHUTDOWN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

        if qnq:
            port_mode = "dot1q-tunnel"

        response = CommandTemplateExecutor(
            self._cli_service,
            add_remove_vlan.SWITCHPORT_MODE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(port_mode=port_mode)
        if self.CHECK_VLAN_MODE_NOT_REJECTED.search(response):
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.SWITCHPORT_REMOVE_TRUNK_AUTO,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(port_mode_trunk="", vlan_range=vlan_range)
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.SWITCHPORT_MODE,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(port_mode=port_mode)
        if qnq:
            self._get_l2_protocol_tunnel_cmd(action_map, error_map).execute_command()

        if "trunk" not in port_mode:
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.SWITCHPORT_ALLOW_VLAN,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(port_mode_access="", vlan_range=vlan_range)

        else:
            vlan_ranges = vlan_range.split(",")
            CommandTemplateExecutor(
                self._cli_service,
                add_remove_vlan.SWITCHPORT_ALLOW_TRUNK_VLAN,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(port_mode_trunk="", vlan_range=vlan_ranges[0])
            for vlans in vlan_ranges[1:]:
                CommandTemplateExecutor(
                    self._cli_service,
                    add_remove_vlan.SWITCHPORT_ALLOW_VLAN,
                    action_map=action_map,
                    error_map=error_map,
                ).execute_command(port_mode_trunk="", vlan_range=vlans)

    def enter_interface_config_id(self, port_name, l2_transport=None):
        l2transport = None
        if l2_transport:
            l2transport = ""
        CommandTemplateExecutor(
            self._cli_service, iface.CONFIGURE_INTERFACE
        ).execute_command(port_name=port_name, l2transport=l2transport)

    def _get_l2_protocol_tunnel_cmd(self, action_map=None, error_map=None):
        return CommandTemplateExecutor(
            self._cli_service,
            add_remove_vlan.L2_TUNNEL,
            action_map=action_map,
            error_map=error_map,
        )
