#coding:utf-8
from typing import Any
from collections import defaultdict


_command_prefix = 'wfb'

def _CommandDict():
    return defaultdict(_CommandDict)


_commands = _CommandDict()


def register(name: str, description: str = '') -> Any:
    '''
    Register a subcommand in the command list

    Args:
        name(str) : The name of the command, separated by '.' (e.g, aicmder.serving)
        description(str) : The description of the specified command showd in the help command, if not description given, this command would not be shown in help command. Default is None.
    '''

    def _warpper(command):
        items = name.split('.')

        com = _commands
        for item in items:
            com = com[item]
        com['_entry'] = command
        if description:
            com['_description'] = description
        return command

    return _warpper


def get_command(name: str) -> Any:
    items = name.split('.')
    com = _commands
    for item in items:
        com = com[item]

    return com['_entry']


def execute():
    import sys
    com = _commands
    for index, _argv in enumerate([_command_prefix] + sys.argv[1:]):
        if _argv not in com:
            break
        com = com[_argv]
    else:
        index += 1

    return com['_entry']().execute(sys.argv[index:])


def help_str(str):
    return '    {:<15}        {}\n'.format('', str)
