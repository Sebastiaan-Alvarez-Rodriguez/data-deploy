import argparse

import os
import sys


'''Python CLI module to deploy data on metareserve-allocated resources.'''

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) # Appends main project root as importpath.

import data_deploy


def _get_modules():
    import data_deploy.cli.clean as clean
    import data_deploy.cli.deploy as deploy
    import data_deploy.cli.plugin as plugin
    return [deploy, clean, plugin]


def generic_args(parser):
    '''Configure arguments important for all modules (install, uninstall, start, stop) here.'''
    parser.add_argument('--key-path', dest='key_path', type=str, default=None, help='Path to ssh key to access nodes.')


def subparser(parser):
    '''Register subparser modules.'''
    generic_args(parser)
    subparsers = parser.add_subparsers(help='Subcommands', dest='command')
    return [x.subparser(subparsers) for x in _get_modules()]


def deploy(mainparser, parsers, args):
    '''Processing of deploy commandline args occurs here.'''
    for parsers_for_module, module in zip(parsers, _get_modules()):
        if module.deploy_args_set(args):
            return module.deploy(parsers_for_module, args)
    mainparser.print_help()
    return False


def main():
    parser = argparse.ArgumentParser(
        prog='data-deploy',
        formatter_class=argparse.RawTextHelpFormatter,
        description='Deploy data on clusters'
    )
    retval = True
    parsers = subparser(parser)

    args = parser.parse_args()
    retval = deploy(parser, parsers, args)

    if isinstance(retval, bool):
        exit(0 if retval else 1)
    elif isinstance(retval, int):
        exit(retval)
    else:
        exit(0 if retval else 1)


if __name__ == '__main__':
    main()