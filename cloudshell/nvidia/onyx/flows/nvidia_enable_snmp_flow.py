#!/usr/bin/python
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.nvidia.onyx.command_actions.enable_disable_snmp_actions import (
    EnableDisableSnmpActions,
)


class NvidiaEnableSnmpFlow:
    DEFAULT_SNMP_VIEW = "quali_snmp_view"
    DEFAULT_SNMP_GROUP = "quali_snmp_group"

    def __init__(self, cli_handler, logger):
        """Enable snmp flow.

        :param cli_handler:
        :param logger:
        :return:
        """
        self._logger = logger
        self._cli_handler = cli_handler

    def enable_flow(self, snmp_parameters):
        if "3" not in snmp_parameters.version and not snmp_parameters.snmp_community:
            message = "SNMP community cannot be empty"
            self._logger.error(message)
            raise Exception(message)

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
                if "3" in snmp_parameters.version:
                    current_snmp_user = snmp_actions.get_current_snmp_user()
                    if not snmp_actions.check_snmp_user_exists(
                        current_snmp_user, snmp_parameters.snmp_user
                    ):
                        snmp_parameters.validate()

                        priv_protocol = (
                            snmp_parameters.snmp_private_key_protocol.lower()
                        )
                        snmp_actions.create_snmp_v3_user(
                            snmp_user=snmp_parameters.snmp_user,
                            snmp_password=snmp_parameters.snmp_password,
                            auth_protocol=snmp_parameters.snmp_auth_protocol.lower(),
                            priv_protocol=priv_protocol,
                            snmp_priv_key=snmp_parameters.snmp_private_key,
                        )
                        snmp_actions.enable_snmp_v3(snmp_user=snmp_parameters.snmp_user)
                    else:
                        return
                else:
                    current_snmp_config = snmp_actions.get_current_snmp_config()
                    if not snmp_actions.check_snmp_community_exists(
                        current_snmp_config, snmp_parameters.snmp_community
                    ):
                        snmp_actions.create_snmp_community(
                            snmp_parameters.snmp_community, snmp_parameters.is_read_only
                        )
                    else:
                        self._logger.debug(
                            "SNMP Community '{}' already configured".format(
                                snmp_parameters.snmp_community
                            )
                        )
                        return
            self._logger.info("Start verification of SNMP config")
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                # Reentering config mode to perform commit for IOS-XR
                updated_snmp_actions = EnableDisableSnmpActions(
                    config_session, self._logger
                )
                if isinstance(snmp_parameters, SNMPV3Parameters):
                    updated_snmp_user = updated_snmp_actions.get_current_snmp_user()
                    if not snmp_actions.check_snmp_user_exists(
                        updated_snmp_user, snmp_parameters.snmp_user
                    ):
                        raise Exception(
                            self.__class__.__name__,
                            "Failed to create SNMP v3 Configuration."
                            + " Please check Logs for details",
                        )
                else:
                    updated_snmp_communities = (
                        updated_snmp_actions.get_current_snmp_config()
                    )
                    if not snmp_actions.check_snmp_community_exists(
                        updated_snmp_communities, snmp_parameters.snmp_community
                    ):
                        raise Exception(
                            self.__class__.__name__,
                            "Failed to create SNMP community."
                            + " Please check Logs for details",
                        )
