#!/usr/bin/python

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.nvidia.onyx.command_templates import configuration, iface


class IFaceActions:
    def __init__(self, cli_service, logger):
        """Add remove vlan.

        :param cli_service: config mode cli_service
        :type cli_service: cloudshell.cli.service.cli_service_impl.CliServiceImpl
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def get_port_name(self, port):
        """Get port name from port resource full name.

        :param port: port resource full address
            (PerfectSwitch/Chassis 0/FastEthernet0-23)
        :return: port name (FastEthernet0/23)
        :rtype: string
        """
        if not port:
            err_msg = "Failed to get port name."
            self._logger.error(err_msg)
            raise Exception("get_port_name", err_msg)

        temp_port_name = port.split("/")[-1]
        if "port channel" in temp_port_name.lower():
            port_channel_id = temp_port_name.lower().replace("port channel", "")
            temp_port_name = f"port channel {port_channel_id}"
        else:
            temp_port_name = temp_port_name.replace("-", "/")
            temp_port_name = temp_port_name.lower().replace("eth", "ethernet ")
        self._logger.info(f"Interface name validation OK, port name = {temp_port_name}")
        return temp_port_name

    def get_current_interface_config(self, port_name, action_map=None, error_map=None):
        """Retrieve current interface configuration.

        :param port_name:
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :return: str
        """
        result = CommandTemplateExecutor(
            self._cli_service,
            iface.SHOW_RUNNING,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(port_name=port_name)
        cmd = iface.SHOW_RUNNING.get_command(port_name=port_name)
        return result.replace(f"{cmd} ", "")

    def enter_iface_config_mode(self, port_name):
        """Enter configuration mode for specific interface.

        :param port_name: interface name
        :return:
        """
        CommandTemplateExecutor(
            self._cli_service, iface.CONFIGURE_INTERFACE
        ).execute_command(port_name=port_name)

    def clean_interface_switchport_config(self, action_map=None, error_map=None):
        """Remove current switchport configuration from interface.

        :param current_config: current interface configuration
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        self._logger.debug("Start cleaning interface switchport configuration")

        CommandTemplateExecutor(
            self._cli_service,
            configuration.NO_SWITCHPORT_MODE,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()
        CommandTemplateExecutor(
            self._cli_service,
            configuration.NO_SWITCHPORT_TRUNK_VLAN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()
        CommandTemplateExecutor(
            self._cli_service,
            configuration.NO_SWITCHPORT_ACCESS_VLAN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()
        self._logger.debug("Completed cleaning interface switchport configuration")
