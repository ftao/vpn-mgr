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
    install_requires=[
        'docopt',
        'pexpect',
        'web.py',
        'python-dateutil',
        'PyYaml',
    ],
    entry_points = {
        'console_scripts': [
            'vpnmgr-cli = vpnmgr.cli:main',
            'vpnmgr-web = vpnmgr.webui.api:main',
    #        'vpnmgr-agent = vpnmgr.agent:main',
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
