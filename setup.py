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
    dependency_links = ['https://github.com/tazjel/python-ifcfg/tarball/master#egg=python-ifcfg'],
    install_requires=[
        'docopt',
        'python-ifcfg',
        'pexpect'
    ],
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
