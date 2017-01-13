from setuptools import setup

setup(
    name='evohome-cli',
    version='0.1.0',
    packages=['evocli'],
    include_package_data=True,
    install_requires=[
        'click', 'evohomeclient', 'pyyaml'
    ],
    entry_points={ 
        'console_scripts': [ 
            'evoc = evocli.__main__:cli'
            ]
        }
)
