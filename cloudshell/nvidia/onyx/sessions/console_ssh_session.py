#!/usr/bin/python

from cloudshell.cli.session.ssh_session import SSHSession


class ConsoleSSHSession(SSHSession):
    SESSION_TYPE = "CONSOLE_SSH"

    def __init__(
        self,
        host,
        username,
        password,
        port=None,
        on_session_start=None,
        *args,
        **kwargs
    ):
        super().__init__(
            host, username, password, port, on_session_start, *args, **kwargs
        )

    def connect(self, prompt, logger):
        """Connect to device through ssh.

        :param prompt: expected string in output
        :param logger: logger
        """
        try:
            super().connect(prompt, logger)
        except Exception:
            self.disconnect()
            raise
