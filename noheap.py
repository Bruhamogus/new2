import os
import sys
import time
from setuptools import setup, Extension
import tempfile
import subprocess
import argparse

GREEN_BLACK_BANNER = """
\033[1;32;40m
888b      88               88        88                                       
8888b     88               88        88                                       
88 `8b    88               88        88                                       
88  `8b   88   ,adPPYba,   88aaaaaaaa88   ,adPPYba,  ,adPPYYba,  8b,dPPYba,   
88   `8b  88  a8"     "8a  88""""""""88  a8P_____88  ""     `Y8  88P'    "8a  
88    `8b 88  8b       d8  88        88  8PP"""""""  ,adPPPPP88  88       d8  
88     `8888  "8a,   ,a8"  88        88  "8b,   ,aa  88,    ,88  88b,   ,a8"  
88      `888   `"YbbdP"'   88        88   `"Ybbd8"'  `"8bbdP"Y8  88`YbbdP"'   
                                                                 88           
                                                                 88           
\033[0m
"""

C_CODE = """
#include <Python.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

static PyObject* overflow_function(PyObject* self, PyObject* args) {
    printf("Starting heap buffer overflow...\\n");

    // Allocate a small buffer
    char* buffer = (char*)malloc(10 * sizeof(char));
    if (buffer == NULL) {
        return PyErr_NoMemory();
    }

    // Overflow the buffer
    for (int i = 0; i < 20; i++) {
        buffer[i] = 'A' + i;
    }

    // Free the buffer
    free(buffer);

    Py_RETURN_NONE;
}

static PyMethodDef OverflowMethods[] = {
    {"overflow_function", overflow_function, METH_VARARGS, "Execute a heap buffer overflow."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef overflowmodule = {
    PyModuleDef_HEAD_INIT,
    "overflow",
    NULL,
    -1,
    OverflowMethods
};

PyMODINIT_FUNC PyInit_overflow(void) {
    return PyModule_Create(&overflowmodule);
}
"""

version = "1.0"

def create_c_extension():
    with tempfile.TemporaryDirectory() as temp_dir:
        c_file = os.path.join(temp_dir, 'overflow.c')
        with open(c_file, 'w') as f:
            f.write(C_CODE)
        
        setup(
            name="heap_overflow_package",
            version=version,
            packages=['heap_overflow'],
            install_requires=[],
            ext_modules=[Extension('heap_overflow.overflow', sources=[c_file])],
            entry_points={
                'console_scripts': [
                    'heap_overflow=heap_overflow.main:main',
                ],
            },
            author="oz",
            description="A package for heap buffer overflow.",
            long_description="This package is created for educational purposes."
        )
        
        subprocess.check_call([sys.executable, 'setup.py', 'build_ext', '--inplace'], cwd=temp_dir)
        
        for filename in os.listdir(temp_dir):
            if filename.startswith('overflow') and filename.endswith(('.so', '.pyd')):
                module_file = os.path.join(temp_dir, filename)
                os.makedirs('heap_overflow', exist_ok=True)
                target_file = os.path.join('heap_overflow', filename)
                os.replace(module_file, target_file)

def print_banner():
    print(GREEN_BLACK_BANNER)

def overflow_heap_buffer(hos):
    print_banner()
    import heap_overflow.overflow as overflow
    print(f"Executing {hos} heap buffer overflows per second...")
    while True:
        for _ in range(hos):
            overflow.overflow_function()
        time.sleep(1)

def custom_payload(filename):
    print_banner()
    print(f"Executing custom payload from file: {filename}")
    with open(filename, 'r') as file:
        payload = file.read()
        exec(payload)

def main():
    parser = argparse.ArgumentParser(description="Heap Overflow Package")
    parser.add_argument('-t', '--target', type=str, help='Target server')
    parser.add_argument('-hOs', '--heap-overflows-per-second', type=int, default=1, help='Heap overflows per second')
    parser.add_argument('-h', '--help', action='store_true', help='Show available commands')
    parser.add_argument('-p', '--payload', type=str, help='Custom payload file')
    parser.add_argument('-v', '--version', action='store_true', help='Show the version of the package')

    args = parser.parse_args()

    if args.help:
        print("""
        Available commands:
        -t [target server]                : Specify the target server
        -hOs [number]                     : Number of heap overflows per second
        -h                                : Show available commands
        -p [filename]                     : Custom payload file
        -v                                : Show the version of the package
        """)
        return

    if args.version:
        print(f"Heap Overflow Package version {version}")
        return

    if args.payload:
        custom_payload(args.payload)
    else:
        overflow_heap_buffer(args.heap_overflows_per_second)

if __name__ == "__main__":
    if not os.path.exists('heap_overflow/overflow.so') and not os.path.exists('heap_overflow/overflow.pyd'):
        create_c_extension()
    main()
