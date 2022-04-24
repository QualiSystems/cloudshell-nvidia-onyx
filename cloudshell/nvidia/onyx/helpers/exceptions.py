#!/usr/bin/python


class NvidiaBaseException(Exception):
    """Base Nvidia exception."""


class NvidiaSNMPException(NvidiaBaseException):
    """Nvidia enable/disable SNMP configuration exception."""


class NvidiaSaveRestoreException(NvidiaBaseException):
    """Nvidia save/restore configuration exception."""


class NvidiaSaveRestoreStatusException(NvidiaSaveRestoreException):
    """Nvidia save/restore configuration exception."""


class NvidiaConnectivityException(NvidiaBaseException):
    """Nvidia connectivity exception."""


class NvidiaFirmwareException(NvidiaBaseException):
    """Nvidia load firmware exception."""
