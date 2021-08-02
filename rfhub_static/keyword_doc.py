import os
import re
import robot
import shutil
import sys

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from jinja2 import Environment, PackageLoader, select_autoescape, debug
from robot.libdoc import LibDoc
from robot.libraries import STDLIBS
from typing import List, Dict
from urllib.parse import quote
from rfhub_static.version import __version__ as pkg_version

LibDocInst = LibDoc()

def generate_doc_file(lib_file_or_resource: str, out_dir: str, out_file: str, lib_name: str) -> Dict:
    result_dict = {}
    out = StringIO()
    err = StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = LibDocInst.execute_cli([lib_file_or_resource, 'list'], exit=False)
    output_text = out.getvalue().strip()
    output_lines = output_text.split('\n') if output_text != '' else []
    if rc == 0 and len(output_lines) > 0:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with redirect_stdout(out), redirect_stderr(err):
            result = LibDocInst.execute(lib_file_or_resource, out_file, docformat='ROBOT', name=lib_name)
        if result != 0 and os.path.exists(out_file):
            os.remove(out_file)
        if os.path.exists(out_file):
            keywords_list = []
            rel_path = os.path.relpath(out_file, out_dir)
            base_url = quote(rel_path)
            for _line in output_lines:
                _line_url = quote(_line)
                keywords_list.append({
                    "name": _line,
                    "url":  base_url + '#' + _line_url
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


def generate_documentation(in_path: str, out_path: str) -> Dict:
    result_dict = {}
    for root, dirs, files in os.walk(in_path):
        for file in files:
            splitext = os.path.splitext(file)
            if splitext[1] in ['.resource', '.txt', '.py']:
                rel_path = os.path.relpath(root, in_path)
                in_file = os.path.join(root, file)
                output_dir = os.path.normpath(os.path.join(out_path, rel_path))
                out_file = os.path.join(output_dir, splitext[0] + '.html')
                result_dict.update(generate_doc_file(in_file, out_path, out_file, rel_path))
    return result_dict


def generate_doc_builtin(out_path: str) -> Dict:
    result_dict = {}
    for lib in STDLIBS:
        if lib not in ['Easter']:
            file_name_rel = lib + '.html'
            file_path = os.path.join(out_path, file_name_rel)
            result_dict.update(generate_doc_file(lib, out_path, file_path, lib))
    return result_dict


def get_robot_modules() -> List[str]:
    result = []
    exclude_libraries = ['robot', 'rfhub', 'rfhub_static']
    # Get parent directory of 'robot'
    library_base_dir = os.path.dirname(robot.__file__)
    library_base_dir = os.path.dirname(library_base_dir)
    for dir_entry in os.scandir(library_base_dir):
        if not os.path.isdir(dir_entry.path):
            continue
        if not re.match('.*[.]dist-info$', dir_entry.name):
            continue
        if not re.match('^robotframework_*', dir_entry.name) and \
                not re.match('^bssf_btap_bss_robot_lib.*', dir_entry.name):
            continue
        top_level_file = os.path.join(dir_entry.path, 'top_level.txt')
        if os.path.exists(top_level_file):
            with open(top_level_file) as f:
                file_data = f.read()
                file_lines = file_data.split('\n')
                for _line in file_lines:
                    _line = _line.strip()
                    if _line and _line not in exclude_libraries:
                        result.append(_line)
    return result

def generate_doc_libraries(out_path: str) -> None:
    result_dict = {}
    directory_list = get_robot_modules()
    for directory in sorted(directory_list):
        result_dict.update(
            generate_doc_file(directory, out_path, os.path.join(out_path, directory + '.html'), directory))
    return result_dict


def create_index_page(out_path: str, library_list: List, resource_list: List) -> None:
    env = Environment(loader=PackageLoader('rfhub_static'), autoescape=select_autoescape())
    template = env.get_template("twocolumn.html")
    result = template.render(data={"version": pkg_version,
                                   "libraries": library_list,
                                   "resource_files": resource_list
                                  })
    with open(os.path.join(out_path, 'index.html'), 'w') as f:
        f.write(result)
    print('Done')

def do_it(in_path: str, out_path: str):

    if not os.path.exists(in_path):
        print ("ERROR: Specified base path " + in_path + ' does not exist.')
        sys.exit(2)
    if not os.path.isdir(in_path):
        print ("ERROR: Specified base path " + in_path + ' is no directory.')
        sys.exit(2)

    # Cleanup and rebuild output path
    if out_path == '/':
        print("ERROR: Target directory is /.\nWe will not remove the Operating System !!")
        sys.exit(2)

    if os.path.exists(out_path):
        shutil.rmtree(out_path, ignore_errors=False)
    os.makedirs(out_path, exist_ok=True)
    web_static_src = os.path.dirname(os.path.realpath(__file__))
    web_static_src = os.path.join(web_static_src, 'static')
    web_static_dst = os.path.join(out_path, 'static')
    shutil.copytree(web_static_src, web_static_dst)

    builtin_dict = generate_doc_builtin(out_path)
    library_dict = generate_doc_libraries(out_path)
    resource_dict = generate_documentation(in_path, out_path)

    all_libraries = builtin_dict.copy()
    all_libraries.update(library_dict)
    all_libraries_sorted = []
    for key in sorted(all_libraries):
        all_libraries_sorted.append(all_libraries[key])
    all_resources_sorted  = []
    for key in sorted(resource_dict):
        all_resources_sorted.append(resource_dict[key])
    create_index_page(out_path, all_libraries_sorted, all_resources_sorted)

def kw_doc_gen():
    if sys.version_info < (3, 6):
        print(sys.argv[0] + " requires python 3.6 or above")
        sys.exit(1)
    if len(sys.argv) != 3:
        print ("Usage: " + sys.argv[0] + ' <base directory> <documentation directory>')
        sys.exit(2)
    in_path = sys.argv[1]  # "/home/ebertli/gitViews/bscs/eb_robot/lhsj_main/bscs/tests/robotScripts/src/main"
    out_path = sys.argv[2]  # "/home/ebertli/gitViews/bscs/eb_robot/lhsj_main/bscs/tests/robotScripts/src/main/docu"
    do_it(in_path, out_path)

if __name__ == '__main__':
    kw_doc_gen()
