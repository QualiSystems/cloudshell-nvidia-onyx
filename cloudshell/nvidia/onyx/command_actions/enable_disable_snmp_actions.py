#!/usr/bin/python
import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.networking.cisco.command_templates import enable_disable_snmp


class EnableDisableSnmpActions:
    READ_ONLY = "ro"
    READ_WRITE = "rw"

    def __init__(self, cli_service, logger):
        """Reboot actions.

        :param cli_service: config mode cli service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    @staticmethod
    def check_snmp_community_exists(snmp_config, snmp_community):
        """Check if snmp community exists in snmp config.

        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :rtype: bool
        """
        escaped_snmp_community = re.escape(snmp_community)
        if re.search(
            fr"(Read-only\s+communities\S*(\s+\S+)*\s*\b{escaped_snmp_community}\b|"
            fr"Read-write\s+communities\S*(\s+\S+)*\s*\b{escaped_snmp_community}\b)",
            snmp_config,
        ):
            return True

    @staticmethod
    def check_snmp_user_exists(snmp_config, snmp_user):
        """Check if snmp user exists in snmp config.

        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :rtype: bool
        """
        if re.search(
            fr"User\s+name\s+\b{snmp_user}\b",
            snmp_config,
        ):
            return True

    @staticmethod
    def check_snmp_enabled(snmp_config):
        """Check if snmp user exists in snmp config.

        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :rtype: bool
        """
        if re.search(
            r"SNMP\s*enabled\s*\S*\s*yes",
            snmp_config,
        ):
            return True

    def get_current_snmp_config(self, action_map=None, error_map=None):
        """Retrieve current snmp communities.

        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SHOW_SNMP_CONFIG,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def get_current_snmp_user(self, action_map=None, error_map=None):
        """Retrieve current snmp communities.

        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SHOW_SNMP_USER,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def enable_snmp(
        self,
        action_map=None,
        error_map=None,
    ):
        """Enable SNMP on the device.

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.ENABLE_SNMP,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def create_snmp_community(
        self,
        snmp_community,
        is_read_only_community=True,
        action_map=None,
        error_map=None,
    ):
        """Enable SNMP on the device.

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        read_only = self.READ_WRITE
        if is_read_only_community:
            read_only = self.READ_ONLY
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.ENABLE_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(snmp_community=snmp_community, read_only=read_only)

    def enable_snmp_v3(
        self,
        snmp_user,
        snmp_password,
        auth_protocol,
        snmp_priv_key,
        priv_protocol,
        action_map=None,
        error_map=None,
    ):
        """Enable SNMP user on the device.

        :param snmp_user: snmp user
        :param snmp_password: snmp password
        :param snmp_priv_key: snmp priv key
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        result = CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.ENABLE_SNMP_USER,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(
            snmp_user=snmp_user,
            snmp_password=snmp_password,
            auth_protocol=auth_protocol,
            snmp_priv_key=snmp_priv_key,
            priv_protocol=priv_protocol,
        )
        return result

    def set_snmp_user_permissions(self, snmp_user, action_map=None, error_map=None):
        """Set SNMP user permissions.

        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SET_SNMP_USER_PERMISSIONS,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(snmp_user=snmp_user)

    def delete_snmp_community(self, snmp_community, action_map=None, error_map=None):
        """Disable SNMP community on the device.

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.DISABLE_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(snmp_community=snmp_community)

    def remove_snmp_user(self, snmp_user, action_map=None, error_map=None):
        """Disable SNMP user on the device.

        :param snmp_user: snmp v3 user name
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        result = CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.DISABLE_SNMP_USER,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(snmp_user=snmp_user)
        return result
