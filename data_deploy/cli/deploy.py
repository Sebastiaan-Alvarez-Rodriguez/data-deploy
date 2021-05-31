import rados_deploy.internal.defaults.deploy as defaults
import rados_deploy.cli.util as _cli_util

from rados_deploy.internal.util.printer import *

'''CLI module to deploy data on a cluster.'''

def subparser(subparsers):
    '''Register subparser modules'''
    deployparser = subparsers.add_parser('deploy', help='deploy RADOS-Ceph on a cluster.')
    deployparser.add_argument('paths', metavar='paths', nargs='+', help='Data to transmit to the remote. Pointed locations can be files or directories. Separate locations using spaces.')
    
    deployparser.add_argument('--admin', metavar='id', dest='admin_id', type=int, default=None, help='ID of the node that will be the Ceph admin node.')
    deployparser.add_argument('--strategy', metavar='strategy', type=str, default=defaults.strategy(), help='Strategy to deploy data (default={}). Must be one of {}'.format(defaults.mountpoint_path()))
    deployparser.add_argument('--osd-op-threads', metavar='amount', dest='osd_op_threads', type=int, default=defaults.osd_op_threads(), help='Number of op threads to use for each OSD (default={}). Make sure this number is not greater than the amount of cores each OSD has.'.format(defaults.osd_op_threads()))
    deployparser.add_argument('--osd-pool-size', metavar='amount', dest='osd_pool_size', type=int, default=defaults.osd_pool_size(), help='Fragmentation of objects across this number of OSDs (default={}).'.format(defaults.osd_pool_size()))
    deployparser.add_argument('--placement-groups', metavar='amount', dest='placement_groups', type=int, default=None, help='Amount of placement groups in Ceph. By default, we use the formula `(num osds * 100) / (pool size)`, as found here: https://ceph.io/pgcalc/.'.format(defaults.mountpoint_path()))
    deployparser.add_argument('--silent', help='If set, less boot output is shown.', action='store_true')
    deployparser.add_argument('--retries', metavar='amount', type=int, default=defaults.retries(), help='Amount of retries to use for risky operations (default={}).'.format(defaults.retries()))

    subsubparsers = deployparser.add_subparsers(help='Subsubcommands', dest='subcommand')
    
    memstoreparser = subsubparsers.add_parser('memstore', help='''deploy a memstore cluster.
Memstore stores all data inside the RAM of each Ceph OSD node.''')
    memstoreparser.add_argument('--storage-size', metavar='amount', dest='storage_size', type=str, default=None, help='Amount of bytes of RAM to allocate for storage with memstore (default={}). Value should not be greater than the amount of RAM available on each OSD node.'.format(defaults.memstore_storage_size()))
    
    bluestoreparser = subsubparsers.add_parser('bluestore', help='''deploy a bluestore cluster.
Bluestore stores all data on a separate device, using its own filesystem.
Each node must provide extra info:
 - device_path: Path to storage device, e.g. "/dev/nvme0n1p4".''')
    bluestoreparser.add_argument('--device-path', metavar='path', dest='device_path', type=str, default=None, help='Overrides "device_path" specification for all nodes.')
    
    return [deployparser, memstoreparser, bluestoreparser]

def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'deploy'

def deploy(parsers, args):
    if args.subcommand == 'memstore':
        from rados_deploy.deploy import memstore
        reservation = _cli_util.read_reservation_cli()
        return memstore(reservation, args.install_dir, args.key_path, args.admin_id, mountpoint_path=args.mountpoint, osd_op_threads=args.osd_op_threads, osd_pool_size=args.osd_pool_size, placement_groups=args.placement_groups, storage_size=args.storage_size, silent=args.silent, retries=args.retries)[0] if reservation else False
    elif args.subcommand == 'bluestore':
        from rados_deploy.deploy import bluestore
        reservation = _cli_util.read_reservation_cli()
        return bluestore(reservation, args.install_dir, args.key_path, args.admin_id, mountpoint_path=args.mountpoint, osd_op_threads=args.osd_op_threads, osd_pool_size=args.osd_pool_size, placement_groups=args.placement_groups, device_path=args.device_path, silent=args.silent, retries=args.retries)[0] if reservation else False
    else: # User did not specify what type of storage type to use.
        printe('Did not provide a storage type (e.g. bluestore).')
        parsers[0].print_help()
        return False