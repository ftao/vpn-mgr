from setuptools import setup, find_packages

version = '0.1'

setup(
    name = 'vpn-mgr',
    version = version,
    packages = find_packages(),

    author = 'Tao Fei',
    author_email = 'filia.tao@gmail.com',
    license = 'GPLv3',
    description = 'VPN Server Manage Tool',
    url='https://github.com/ftao/vpn-mgr',
    dependency_links = ['https://github.com/ftao/python-ifcfg/tarball/master#egg=ifcfg'],
    install_requires=[
        'docopt',
        'ifcfg',
        'pexpect',
        'web.py',
        'pyzmq',
        'python-dateutil',
    ],
    entry_points = {
        'console_scripts': [
            'vpnmgr-cli = vpnmgr.cli:main',
            'vpnmgr-web = vpnmgr.webapi:main',
            'vpnmgr-agent = vpnmgr.agent:main',
            'vpnmgr-master = vpnmgr.master:main',
        ],
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Linux Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe = False,
)
