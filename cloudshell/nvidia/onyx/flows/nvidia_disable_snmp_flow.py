#!/usr/bin/python
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.nvidia.onyx.command_actions.enable_disable_snmp_actions import (
    EnableDisableSnmpActions,
)


class NvidiaDisableSnmpFlow:
    def __init__(self, cli_handler, logger):
        """Enable snmp flow.

        :param cli_handler:
        :type cli_handler: CiscoCliHandler
        :param logger:
        :return:
        """
        self._cli_handler = cli_handler
        self._logger = logger

    def disable_flow(self, snmp_parameters):
        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
                if "3" in snmp_parameters.version:
                    current_snmp_user = snmp_actions.get_current_snmp_user()
                    if snmp_actions.check_snmp_user_exists(
                        current_snmp_user, snmp_parameters.snmp_user
                    ):
                        snmp_actions.remove_snmp_user(snmp_parameters.snmp_user)
                else:
                    self._logger.debug("Start Disable SNMP")
                    snmp_actions.delete_snmp_community(snmp_parameters.snmp_community)
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                # Reentering config mode to perform commit for IOS-XR
                updated_snmp_actions = EnableDisableSnmpActions(
                    config_session, self._logger
                )
                if isinstance(snmp_parameters, SNMPV3Parameters):
                    updated_snmp_user = updated_snmp_actions.get_current_snmp_user()
                    if snmp_actions.check_snmp_user_exists(
                        updated_snmp_user, snmp_parameters.snmp_user
                    ):
                        raise Exception(
                            self.__class__.__name__,
                            "Failed to remove SNMP v3 Configuration."
                            + " Please check Logs for details",
                        )
                else:
                    updated_snmp_communities = (
                        updated_snmp_actions.get_current_snmp_config()
                    )
                    if snmp_actions.check_snmp_community_exists(
                        updated_snmp_communities, snmp_parameters.snmp_community
                    ):
                        raise Exception(
                            self.__class__.__name__,
                            "Failed to remove SNMP community."
                            + " Please check Logs for details",
                        )
