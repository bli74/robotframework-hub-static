"""
To push a new version to PyPi, update the version number
in rfhub_static/version.py and then run the following commands:

    $ python setup.py sdist
    $ python3 -m twine upload dist/*

"""
from setuptools import setup

__version__: str = "0.0.0"
filename: str = 'rfhub_static/version.py'
exec(open(filename).read())

setup_requires_packages: list = ['wheel']
install_requires_packages: list = [
    'Jinja2>=2.11.3',
    'robotframework>=2.8.5'
]
test_requires_packages: list = [
    'robotframework-requests'
]


setup(
    name='robotframework-hub-static',
    version=__version__,
    author='Bryan Oakley',
    author_email='bryan.oakley@gmail.com',
    maintainer='Bert Lindemann',
    maintainer_email='bert.lindemann@gmail.com',
    url='https://github.com/bli74/robotframework-hub/',
    keywords='robotframework',
    license='Apache License 2.0',
    description='Create robot keyword documentation as static HTML',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    zip_safe=True,
    include_package_data=True,
    python_requires=">=3.8",
    setup_requires=setup_requires_packages,
    install_requires=install_requires_packages,
      extras_require={
          'test': test_requires_packages,
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
        'rfhub_static',
    ],
    package_data={
        # Include style sheets, JavaScript code and HTML template files
        "": ["static/*", "static/css/*", "static/js/*", "templates/*"],
    },
    scripts=[],
    entry_points={
        'console_scripts': [
            "keyword_doc = rfhub_static.keyword_doc:kw_doc_gen"
        ]
    }
)
