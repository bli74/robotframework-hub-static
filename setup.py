"""
To push a new version to PyPi, update the version number
in rfhub/version.py and then run the following commands:

    $ python setup.py sdist
    $ python3 -m twine upload dist/*

"""
from setuptools import setup

__version__: str = "0.0.0"
filename: str = 'rfhub/version.py'
exec(open(filename).read())

setup_requires_packages: list = ['wheel']
install_requires_packages: list = [
    'Flask>=1.1.1',
    'Jinja2>=2.11.3',
    'MarkupSafe>=0.23',
    'PyYAML>=5.4',
    'Werkzeug>=0.15.3',
    'argh>=0.25.0',
    'itsdangerous>=0.24',
    'tornado>=6.0.3',
    'pathtools3>=0.2.1',
    'requests>=2.20.0',
    'robotframework>=2.8.5',
    'robotframework-requests>=0.5.0',
    'robotframework-seleniumlibrary>=4.0.0',
    'watchdog>=0.9.0'
]
test_requires_packages: list = ['coverage']

setup(
    name='robotframework-hub-bli',
    version=__version__,
    author='Bryan Oakley',
    author_email='bryan.oakley@gmail.com',
    maintainer='Bert Lindemann',
    maintainer_email='bert.lindemann@gmail.com',
    url='https://github.com/bli74/robotframework-hub/',
    keywords='robotframework',
    license='Apache License 2.0',
    description='Webserver for robot framework assets',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    zip_safe=True,
    include_package_data=True,
    python_requires=">=3.6",
    setup_requires=setup_requires_packages,
    install_requires=install_requires_packages,
    extras_require={
        'test': test_requires_packages
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Framework :: Robot Framework",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Intended Audience :: Developers",
    ],
    packages=[
        'rfhub',
        'rfhub.blueprints',
        'rfhub.blueprints.api',
        'rfhub.blueprints.doc',
        'rfhub.blueprints.dashboard',
    ],
    scripts=[],
    entry_points={
        'console_scripts': [
            "rfhub = rfhub.__main__:main"
        ]
    }
)
