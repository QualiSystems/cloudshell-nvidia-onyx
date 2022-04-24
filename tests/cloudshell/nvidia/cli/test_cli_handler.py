from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from cloudshell.cli.service.cli import CLI

from cloudshell.nvidia.onyx.cli.nvidia_cli_handler import NvidiaCliHandler
from cloudshell.nvidia.onyx.cli.nvidia_command_modes import (
    ConfigCommandMode,
    DefaultCommandMode,
    EnableCommandMode,
)


class TestMellanoxSystemActions(TestCase):
    REGULAR_PROMPT = "Mellanox-Switch [standalone: master] # "
    CONFIG_PROMPT = "Mellanox-Switch [standalone: master] (config)#"

    def set_up(self):
        ConfigCommandMode.ENTER_CONFIG_RETRY_TIMEOUT = 0.5
        cli_conf = MagicMock()
        cli_conf.cli_tcp_port = "22"
        cli_conf.cli_connection_type = "SSH"
        return NvidiaCliHandler(CLI(), cli_conf, Mock())

    def test_default_mode(self):
        cli_handler = self.set_up()
        self.assertIsInstance(cli_handler.default_mode, DefaultCommandMode)

    def test_enable_mode(self):
        cli_handler = self.set_up()
        self.assertIsInstance(cli_handler.enable_mode, EnableCommandMode)

    def test_config_mode(self):
        cli_handler = self.set_up()
        self.assertIsInstance(cli_handler.config_mode, ConfigCommandMode)

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch(
        "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value=""
    )
    @patch("cloudshell.cli.session.ssh_session.SSHSession._receive_all")
    def test_enter_config_mode_with_lock(self, recv_mock, cb_mock, paramiko_mock):
        recv_mock.side_effect = [
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            "Mellanox-Switch [standalone: master] # configuration Locked",
            f"{self.CONFIG_PROMPT}",
            f"{self.CONFIG_PROMPT}",
            f"{self.CONFIG_PROMPT}",
            f"{self.CONFIG_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
        ]
        cli_handler = self.set_up()
        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch(
        "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value=""
    )
    @patch("cloudshell.cli.session.ssh_session.SSHSession._receive_all")
    def test_enter_config_mode_with_multiple_retries(
        self, recv_mock, cb_mock, paramiko_mock
    ):
        locked_message = """Boogie#
        configuration Locked
        Boogie#"""
        recv_mock.side_effect = [
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            f"{self.CONFIG_PROMPT}",
            f"{self.CONFIG_PROMPT}",
            f"{self.CONFIG_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
        ]
        cli_handler = self.set_up()
        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch(
        "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value=""
    )
    @patch("cloudshell.cli.session.ssh_session.SSHSession._receive_all")
    def test_enter_config_mode_regular(self, recv_mock, cb_mock, paramiko_mock):
        recv_mock.side_effect = [
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.CONFIG_PROMPT}",
            f"{self.CONFIG_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
        ]
        cli_handler = self.set_up()
        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch(
        "cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value=""
    )
    @patch("cloudshell.cli.session.ssh_session.SSHSession._receive_all")
    def test_enter_config_mode_fail(self, recv_mock, cb_mock, paramiko_mock):
        error_message = (
            "Failed to create new session for type SSH, see logs for details"
        )
        locked_message = f"""{self.REGULAR_PROMPT}
        configuration Locked
        {self.REGULAR_PROMPT}"""
        recv_mock.side_effect = [
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            f"{self.CONFIG_PROMPT}",
            f"{self.REGULAR_PROMPT}",
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            locked_message,
            locked_message,
        ]
        cli_handler = self.set_up()

        try:
            with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
                session.send_command("")
        except Exception as e:
            self.assertTrue(error_message in e.args)
