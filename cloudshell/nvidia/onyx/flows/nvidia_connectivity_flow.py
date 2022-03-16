#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.shell.flows.connectivity.basic_flow import AbstractConnectivityFlow

from cloudshell.nvidia.onyx.command_actions.add_remove_vlan_actions import (
    AddRemoveVlanActions,
)
from cloudshell.nvidia.onyx.command_actions.iface_actions import IFaceActions
from cloudshell.shell.flows.connectivity.models.connectivity_model import ConnectivityActionModel
from cloudshell.shell.flows.connectivity.models.driver_response import ConnectivityActionResult
from cloudshell.shell.flows.connectivity.parse_request_service import ParseConnectivityRequestService


class NvidiaConnectivityFlow(AbstractConnectivityFlow):

    def __init__(
        self,
        cli_handler,
        logger,
    ):
        vlan_service = ParseConnectivityRequestService(is_multi_vlan_supported=True, is_vlan_range_supported=True)
        super(NvidiaConnectivityFlow, self).__init__(vlan_service, logger)
        self._cli_handler = cli_handler

    def _get_vlan_actions(self, config_session):
        return AddRemoveVlanActions(config_session, self._logger)

    def _get_iface_actions(self, config_session):
        return IFaceActions(config_session, self._logger)

    def _set_vlan(self, action: ConnectivityActionModel) -> ConnectivityActionResult:
        """Configures VLANs on multiple ports or port-channels.

        :param vlan_range: VLAN or VLAN range
        :param port_mode: mode which will be configured on port.
            Possible Values are trunk and access
        :param port_name: full port name
        :param qnq:
        :param c_tag:
        :return:
        """
        success = False
        port_name = action.action_target.name
        vlan_range = action.connection_params.vlan_id
        port_mode = action.connection_params.mode.value.lower()
        qnq = action.connection_params.vlan_service_attrs.qnq
        self._logger.info("Add VLAN(s) {} configuration started".format(vlan_range))

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            en_iface_action = self._get_iface_actions(enable_session)
            port_name = en_iface_action.get_port_name(port_name)
            en_vlan_action = self._get_vlan_actions(enable_session)
            with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                iface_action = self._get_iface_actions(config_session)
                vlan_actions = self._get_vlan_actions(config_session)
                vlan_actions.create_vlan(vlan_range)
                vlan_actions.set_vlan_to_interface(vlan_range, port_mode, port_name, qnq)
                current_config = iface_action.get_current_interface_config(port_name)
            if en_vlan_action.verify_interface_has_vlan_assigned(
                    vlan_range, current_config
                ):
                    success = True
            if not success:
                ConnectivityActionResult.fail_result(
                    action,
                    f"[FAIL] VLAN(s) {vlan_range} configuration failed"
                )

        self._logger.info(
            "VLAN(s) {} configuration completed successfully".format(vlan_range)
        )
        return ConnectivityActionResult.success_result(
            action,
            f"[ OK ] VLAN(s) {vlan_range} configuration completed successfully"
        )

    def _remove_vlan(self, action: ConnectivityActionModel) -> ConnectivityActionResult:
        """Remove configuration of VLANs on multiple ports or port-channels.

        """
        port_name = action.action_target.name
        vlan_range = action.connection_params.vlan_id

        self._logger.info("Remove Vlan {} configuration started".format(vlan_range))
        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            en_iface_action = self._get_iface_actions(enable_session)
            port_name = en_iface_action.get_port_name(port_name)
            vlan_action = self._get_vlan_actions(enable_session)
            with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                iface_action = self._get_iface_actions(config_session)
                iface_action.enter_iface_config_mode(port_name)
                iface_action.clean_interface_switchport_config()
                current_config = iface_action.get_current_interface_config(port_name)
            if vlan_action.verify_interface_has_no_vlan_assigned(
                current_config
            ):
                return ConnectivityActionResult.fail_result(
                    action,
                    f"[FAIL] VLAN(s) {vlan_range} removal failed"
                )

        self._logger.info(
            "VLAN(s) {} removal completed successfully".format(vlan_range)
        )
        return ConnectivityActionResult.success_result(action, f"[ OK ] VLAN(s) {vlan_range} removal completed successfully")

    def _remove_vlan_from_interface(self, port_name, iface_actions):
        current_config = iface_actions.get_current_interface_config(port_name)
        iface_actions.enter_iface_config_mode(port_name)
        iface_actions.clean_interface_switchport_config(current_config)
