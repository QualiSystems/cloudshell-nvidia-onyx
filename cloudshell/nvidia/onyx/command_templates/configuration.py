# !/usr/bin/python

from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

SAVE_CONFIG = CommandTemplate("configuration write to {filename} no-switch")

DELETE_CONFIG = CommandTemplate("configuration delete {filename}")

GENERATE_TXT_CONFIG = CommandTemplate(
    "configuration text generate file {filename} save {filename}.txt"
)  # noqa: E501

APPLY_TXT_CONFIG = CommandTemplate("configuration text file {filename} apply")

UPLOAD = CommandTemplate(
    "configuration upload {src} {dst} [vrf {vrf}]",
    action_map=OrderedDict(
        {
            r"Type\s*\S*yes\S*\s*to\s*confirm": lambda session, logger: session.send_line(  # noqa: E501
                "yes", logger
            ),
        }
    ),
)

DOWNLOAD = CommandTemplate(
    "configuration fetch {path} [vrf {vrf}]",
    action_map=OrderedDict(
        {
            r"Type\s*\S*yes\S*\s*to\s*confirm": lambda session, logger: session.send_line(  # noqa: E501
                "yes", logger
            ),
        }
    ),
)

SWITCH_CONFIG = CommandTemplate(
    "configuration switch-to {filename}",
    action_map=OrderedDict(
        {
            r"Type\s*\S*yes\S*\s*to\s*confirm": lambda session, logger: session.send_line(  # noqa: E501
                "yes", logger
            ),
        }
    ),
)

NO = CommandTemplate("no {command}")

NO_SWITCHPORT_MODE = CommandTemplate("no switchport mode")

NO_SWITCHPORT_TRUNK_VLAN = CommandTemplate("no switchport trunk allowed-vlan")

NO_SWITCHPORT_ACCESS_VLAN = CommandTemplate("no switchport access vlan")
