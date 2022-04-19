#!/usr/bin/python
import os
import re

from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow
from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload
from cloudshell.snmp.autoload.service.port_mapper import PortMappingService
from cloudshell.snmp.autoload.snmp_if_table import SnmpIfTable


class NvidiaSnmpAutoloadFlow(AbstractAutoloadFlow):
    MIBS_FOLDER = os.path.join(os.path.dirname(__file__), os.pardir, "mibs")

    def __init__(self, logger, snmp_handler):
        super().__init__(logger)
        self._snmp_handler = snmp_handler

    def _autoload_flow(self, supported_os, resource_model):
        SnmpIfTable.PORT_CHANNEL_NAME = ["po"]
        SnmpIfTable.PORT_VALID_TYPE = re.compile(
            r"ethernet|other|propPointToPointSerial|fastEther|opticalChannel|^otn",
            re.IGNORECASE,
        )
        PortMappingService.PORT_EXCLUDE_RE = re.compile(
            r"stack|engine|management|mgmt|null|voice|foreign|"
            r"cpu|TenGigECtrlr\S*|control\s*ethernet\s*port|console\s*port",
            re.IGNORECASE,
        )
        with self._snmp_handler.get_service() as snmp_service:
            snmp_service.add_mib_folder_path(self.MIBS_FOLDER)
            snmp_service.load_mib_tables(["MELLANOX-PRODUCTS-MIB"])
            nvidia_snmp_autoload = GenericSNMPAutoload(snmp_service, self._logger)
            nvidia_snmp_autoload.entity_table_service.set_port_exclude_pattern(
                r"stack|engine|management|"
                r"mgmt|voice|foreign|cpu|"
                r"control\s*ethernet\s*port|"
                r"usb\s*port|TenGigECtrlr"
                r"\s*timing\s*interface\s*port"
            )

            return nvidia_snmp_autoload.discover(
                supported_os, resource_model, validate_module_id_by_port_name=True
            )
