import os
import re
import shutil
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import List, Dict
from urllib.parse import quote

import robot
from jinja2 import Environment, select_autoescape, FileSystemLoader
from robot.libdoc import LibDoc
from robot.libraries import STDLIBS

from rfhub_static.version import __version__ as pkg_version

libdoc_instance = LibDoc()


def generate_doc_file(lib_file_or_resource: str, out_dir: str, out_file: str, lib_name: str) -> Dict:
    result_dict = {}
    out = StringIO()
    err = StringIO()
    # Check if 'libdoc' is successful and if any keywords are included
    with redirect_stdout(out), redirect_stderr(err):
        rc = libdoc_instance.execute_cli([lib_file_or_resource, 'list'], exit=False)
    output_text = out.getvalue().strip()
    output_lines = output_text.split('\n') if output_text != '' else []
    if rc == 0 and len(output_lines) > 0:
        # The 'libdoc' call was successful and there are keywords
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with redirect_stdout(out), redirect_stderr(err):
            result = libdoc_instance.execute(lib_file_or_resource, out_file, docformat='ROBOT', name=lib_name)
        if result != 0 and os.path.exists(out_file):
            # Remove output file in case of an error
            os.remove(out_file)
        if os.path.exists(out_file):
            keywords_list = []
            rel_path = os.path.relpath(out_file, out_dir)
            base_url = quote(rel_path)
            for _line in sorted(output_lines):
                _line_url = quote(_line)
                keywords_list.append({
                    "name": _line,
                    "url": base_url + '#' + _line_url
                })
            result_dict[lib_name] = {
                "name": lib_name,
                "keywords": keywords_list,
                "path": lib_file_or_resource,
                "url": base_url
            }
            print('Created ' + out_file + ' with ' + str(len(keywords_list)) + ' keywords.')
    out.close()
    err.close()
    return result_dict


def generate_doc_builtin(out_path: str) -> Dict:
    result_dict = {}
    for lib in sorted(STDLIBS):
        if lib not in ['Easter']:
            file_name_rel = lib + '.html'
            file_path = os.path.join(out_path, file_name_rel)
            result_dict.update(generate_doc_file(lib, out_path, file_path, lib))
    return result_dict


def get_robot_modules(package_prefixes: List[str]) -> List[str]:
    result = []
    exclude_libraries = ['robot', 'rfhub', 'rfhub_static']
    # Collect regex to match 'robotframework' and any entry of package_prefixes.
    _package_prefixes_full = []
    for _package_prefix in package_prefixes:
        _package_prefixes_full.append('^' + _package_prefix.replace('-', '[-_]') + '.*[.]dist-info$')
    regex_any_prefix = '(?:%s)' % '|'.join(_package_prefixes_full)
    # Get parent directory of directory 'robot'
    library_base_dir = os.path.dirname(robot.__file__)
    library_base_dir = os.path.dirname(library_base_dir)
    for dir_entry in sorted(os.listdir(library_base_dir)):
        dir_entry_path = os.path.join(library_base_dir, dir_entry)
        # Just consider directories, that match any prefixes
        if os.path.isdir(dir_entry_path) \
                and re.match(regex_any_prefix, dir_entry):
            # Read library name from package metadata
            top_level_file = os.path.join(dir_entry_path, 'top_level.txt')
            if os.path.exists(top_level_file):
                with open(top_level_file) as f:
                    file_data = f.read()
                    file_lines = file_data.split('\n')
                    for _line in file_lines:
                        _line = _line.strip()
                        if _line and _line not in exclude_libraries:
                            result.append(_line)
    return result


def generate_doc_libraries(out_path: str, package_prefixes: List[str]) -> Dict:
    result_dict = {}
    directory_list = get_robot_modules(package_prefixes)
    for directory in sorted(directory_list):
        result_dict.update(
            generate_doc_file(directory, out_path, os.path.join(out_path, directory + '.html'), directory))
    return result_dict

def get_resource_file_list(directory_path: str, exclude_patterns: List[str]) -> List[str]:
    _ignore_file = os.path.join(directory_path, ".rfhubignore")
    _exclude_patterns = exclude_patterns.copy()
    if os.path.exists(_ignore_file):
        # noinspection PyBroadException
        try:
            with open(_ignore_file, "r") as f:
                for line in f.readlines():
                    line = line.strip()
                    if re.match(r'^\s*#', line):
                        continue
                    if len(line) > 0:
                        _exclude_patterns.append(line)
        except:
            pass
    # Get list of files and directories, remove matching exclude patterns
    dir_entry_list = os.listdir(directory_path)
    dir_entry_list = [x for x in dir_entry_list if not any(re.search(r, x) for r in _exclude_patterns)]
    file_list = []
    for entry_name in dir_entry_list:
        entry_path = os.path.join(directory_path, entry_name)
        if os.path.isdir(entry_path) \
                and not entry_name.startswith(".") \
                and os.access(entry_path, os.R_OK):
            file_list += get_resource_file_list (entry_path, exclude_patterns=_exclude_patterns)
        elif not entry_name.startswith("."):
            splitext = os.path.splitext(entry_name)
            if splitext[1] in ['.resource', '.txt', '.py']:
                file_list.append(entry_path)
    return file_list

def generate_documentation(in_path: str, out_path: str) -> Dict:
    file_list = get_resource_file_list(in_path, [])
    result_dict = {}
    in_path_full  = os.path.abspath(in_path)
    out_path_full = os.path.abspath(out_path)
    for file in sorted(file_list):
        splitext = os.path.splitext(os.path.basename(file))
        file_path_full = os.path.abspath(file)
        file_dir_full = os.path.dirname(file_path_full)
        rel_path = os.path.relpath(file_dir_full, in_path_full)
        output_dir = os.path.normpath(os.path.join(out_path_full, rel_path))
        out_file = os.path.join(output_dir, splitext[0] + '.html')
        resource_name = os.path.relpath(file, in_path_full)
        result_dict.update(generate_doc_file(file_path_full, out_path, out_file, resource_name))
    return result_dict


def create_index_page(out_path: str, template_directory: str, library_list: List, resource_list: List) -> None:
    env = Environment(loader=FileSystemLoader(template_directory), autoescape=select_autoescape())
    template = env.get_template("twocolumn.html")
    result = template.render(data={"version": pkg_version,
                                   "libraries": library_list,
                                   "resource_files": resource_list
                                   })
    with open(os.path.join(out_path, 'index.html'), 'w') as f:
        f.write(result)
    print('Done')


def do_it(in_path: str, out_path: str, package_prefixes: List[str]) -> None:
    if not os.path.exists(in_path):
        print("ERROR: Specified base path " + in_path + ' does not exist.')
        sys.exit(2)
    if not os.path.isdir(in_path):
        print("ERROR: Specified base path " + in_path + ' is no directory.')
        sys.exit(2)

    # Cleanup and rebuild output path
    if out_path == '/':
        print("ERROR: Target directory is /.\nWe will not remove the Operating System !!")
        sys.exit(2)

    if os.path.exists(out_path):
        shutil.rmtree(out_path, ignore_errors=False)
    os.makedirs(out_path, exist_ok=True)
    package_base_directory = os.path.dirname(os.path.realpath(__file__))
    template_directory = os.path.join(package_base_directory, 'templates')
    static_src = os.path.join(package_base_directory, 'static')
    static_dst = os.path.join(out_path, 'static')
    shutil.copytree(static_src, static_dst)

    builtin_dict = generate_doc_builtin(out_path)
    library_dict = generate_doc_libraries(out_path, package_prefixes)
    resource_dict = generate_documentation(in_path, out_path)

    all_libraries = builtin_dict.copy()
    all_libraries.update(library_dict)
    all_libraries_sorted = []
    for key in sorted(all_libraries):
        all_libraries_sorted.append(all_libraries[key])
    all_resources_sorted = []
    for key in sorted(resource_dict):
        all_resources_sorted.append(resource_dict[key])
    create_index_page(out_path, template_directory, all_libraries_sorted, all_resources_sorted)


def kw_doc_gen():
    if sys.version_info < (3, 6):
        print(sys.argv[0] + " requires python 3.6 or above")
        sys.exit(1)
    if len(sys.argv) < 3:
        prg_name = os.path.basename(sys.argv[0])
        print('Usage: ' + prg_name + ' <base directory> <documentation directory> [ <library prefix> ... ])\n\n' +
              'base directory:          Top level directory to scan for resource files. \n' +
              'documentation_directory: Directory to store the documentation files.\n' +
              '                         The directory will be cleaned up before the\n' +
              '                         new documentation is created.\n' +
              'library_prefix:          Optional list of Python package prefixes that are\n' +
              '                         scanned for keywords in addition to robot built-in\n' +
              '                         libraries.\n\n' +
              'Examples:\n\n' +
              '   ' + prg_name + '  ~/robot_tests ~/robot_kw_docu\n' +
              '   -> Scans for robot keywords in:\n' +
              '      - robotframework internal libraries\n' +
              '      - python packages starting with "robotframework"\n' +
              '      - robot resource files in all subdirectories of ~/robot_tests \n' +
              '   -> Generates documentation in ~/robot_kw_docu:\n' +
              '      - index.html with table of content\n' +
              '      - <module>.html with keywords of the libraries\n' +
              '      - <path/to/resource>.html with keywords of resource file\n\n' +
              '   -> reads robotframework internal keyword libraries\n' +
              '   -> reads robotframework internal keyword libraries\n' +
              '   -> reads robotframework internal keyword libraries\n' +
              '\n' +
              '   ' + prg_name + '  ~/robot_tests ~/robot_kw_docu bssf_btap_common bssf_btap_fnt\n' +
              '   -> Scans for robot keywords in:\n' +
              '      - robotframework internal libraries\n' +
              '      - python packages starting with "robotframework"\n' +
              '      - python packages starting with "bssf_btap_common" and "bssf_btap_fnt"\n' +
              '      - robot resource files in all subdirectories of ~/robot_tests \n' +
              '   -> Generates documentation in ~/robot_kw_docu:\n' +
              '      - index.html with table of content\n' +
              '      - <module>.html with keywords of the libraries\n' +
              '      - <path/to/resource>.html with keywords of resource file\n\n'
              )
        sys.exit(2)
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    package_prefixes = ['robotframework']
    for package_prefix in sys.argv[3:]:
        package_prefixes.append(package_prefix)
    do_it(in_path, out_path, package_prefixes)


if __name__ == '__main__':
    kw_doc_gen()
