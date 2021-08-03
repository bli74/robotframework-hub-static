# Welcome to Robot Framework Hub Static

## Motivation
This project is based on Robot Framework Hub to generate
keyword documentation for a robotframework environment.

The original Robot Framework Hub needs a running web server
process. There are no artifacts that can be published by a 
CI/CD pipeline.

Here Robot Framework Hub Static can be used. It generates
with ´libdoc´ the documentation for the robot internal 
libraries, additional installed robot libraries and robot
resource files.
Based on the list of the generated HTML files an index page
is created

## Getting started

```
    $ pip install robotframework-hub-static
    $ keyword_doc ${ROOT_PATH_ROBOT_RESOURCES} ${DOCU_DIR}
```

Note:
* robotframework-hub requires python 3.6 or greater
* The documentation directory is cleaned up, use a dedicated
  directory to store the documentation.


## Websites

Source code, screenshots, and additional documentation can be
found here:

* Source code: https://github.com/bli74/robotframework-hub-static

This is a fork of the initial project:

* Source code (updated): https://github.com/bli74/robotframework-hub
* Source code (upstream): https://github.com/boakley/robotframework-hub
* Project wiki: https://github.com/boakley/robotframework-hub/wiki

## Acknowledgements

A huge thank-you to Echo Global Logistics (echo.com) for supporting
the development of this package.
