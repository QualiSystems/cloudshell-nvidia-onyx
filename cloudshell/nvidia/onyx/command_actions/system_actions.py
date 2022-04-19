#!/usr/bin/python

import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.session.session_exceptions import (
    CommandExecutionException,
    ExpectedSessionException,
)

from cloudshell.nvidia.onyx.command_templates import configuration


class SystemActions:
    def __init__(self, cli_service, logger):
        """Reboot actions.

        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def save_config(self, filename, action_map=None, error_map=None):
        output = CommandTemplateExecutor(
            self._cli_service,
            configuration.SAVE_CONFIG,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(filename=filename)
        return output

    def generate_txt_config(self, filename, action_map=None, error_map=None):
        output = CommandTemplateExecutor(
            self._cli_service,
            configuration.GENERATE_TXT_CONFIG,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(filename=filename)
        return output

    def apply_txt_config(self, filename, action_map=None, error_map=None):
        output = CommandTemplateExecutor(
            self._cli_service,
            configuration.APPLY_TXT_CONFIG,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(filename=filename)
        return output

    def upload(
        self,
        source,
        destination,
        vrf=None,
        action_map=None,
        error_map=None,
        timeout=180,
    ):
        """Copy file from device to tftp or vice versa.

        As well as copying inside devices filesystem.
        :param source: source file
        :param destination: destination file
        :param vrf: vrf management name
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :param timeout: session timeout
        :raise Exception:
        """
        if not vrf:
            vrf = None

        output = CommandTemplateExecutor(
            self._cli_service,
            configuration.UPLOAD,
            action_map=action_map,
            error_map=error_map,
            timeout=timeout,
        ).execute_command(src=source, dst=destination, vrf=vrf)

        copy_ok_pattern = (
            r"\d+ bytes copied|copied.*[\[\(].*[1-9][0-9]* bytes.*[\)\]]|"
            r"[Cc]opy complete|[\(\[]OK[\]\)]"
        )
        status_match = re.search(copy_ok_pattern, output, re.IGNORECASE)
        if not status_match:
            match_error = re.search(
                r"%.*|TFTP put operation failed.*|sysmgr.*not supported.*\n",
                output,
                re.IGNORECASE,
            )
            message = "Upload Command failed."
            if match_error:
                self._logger.error(message)
                message += re.sub(r"^%\s+|\\n|\s*at.*marker.*", "", match_error.group())
            else:
                error_match = re.search(r"error.*\n|fail.*\n", output, re.IGNORECASE)
                if error_match:
                    self._logger.error(message)
                    message += error_match.group()
            raise Exception(message)

    def download(self, path, action_map=None, error_map=None):
        """Delete file on the device.

        :param path: path to file
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        """
        CommandTemplateExecutor(
            self._cli_service,
            configuration.DOWNLOAD,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(path=path)

    def override_running(
        self,
        filename,
        action_map=None,
        error_map=None,
        timeout=300,
        reconnect_timeout=1600,
    ):
        """Override running-config.

        :param path: relative path to the file on the remote host
            tftp://server/sourcefile
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
        i.e. handles Invalid Commands errors
        :raise Exception:
        """
        try:
            output = CommandTemplateExecutor(
                self._cli_service,
                configuration.SWITCH_CONFIG,
                action_map=action_map,
                error_map=error_map,
                timeout=timeout,
                check_action_loop_detector=False,
                remove_prompt=True,
            ).execute_command(filename=filename)
            match_error = re.search(r"% \S+.*", output, flags=re.DOTALL)
            if match_error:
                error_str = match_error.group()
                raise CommandExecutionException(
                    "Override_Running",
                    "Configure replace completed with error: \n"
                    + error_str.replace("%", "\n"),
                )
        except ExpectedSessionException as e:
            self._logger.warning(e.args)
            if isinstance(e, CommandExecutionException):
                raise
            self._cli_service.reconnect(reconnect_timeout)

    def shutdown(self):
        """Shutdown the system."""
        pass
