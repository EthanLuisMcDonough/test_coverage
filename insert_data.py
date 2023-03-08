#!/usr/bin/python3

import json
import sqlite3
import os
import re
import subprocess
import sys

def normalize_test_name(test_path):
    return test_path[test_path.find("test/"):].split(".", 1)[0]

def resolve_file_local(path):
    return os.path.join(os.path.dirname(__file__), path)

def log_errors(err):
    with open(resolve_file_local("log.txt"), "a") as file:
        file.write(err + "\n")

def select_options(args, options):
    opts = []
    for i in range(len(args) - 1):
        if args[i] in options:
            opts.append(args[i])
            opts.append(args[i + 1])
    return opts


def gen_todo(con, todo_msg):
    check_res = con.execute("SELECT id FROM todo_message WHERE msg = ?", (todo_msg,))
    check_row = check_res.fetchone()
    if check_row:
        return check_row[0]
    ins_res = con.execute("INSERT INTO todo_message (msg) VALUES (?)", (todo_msg,))
    return ins_res.lastrowid

# options to include in test build if present in test command
include_opt = ["-fopenmp", "-fopenacc"]

# include options
param_opt = ["-I", "-J"]

suffixes = [".f", ".F", ".ff", ".FOR", ".for", ".f77", ".f90", ".F90",
            ".ff90", ".f95", ".F95", ".ff95", ".fpp", ".FPP", ".cuf",
            ".CUF", ".f18", ".F18", ".f03", ".F03", ".f08", ".F08", ".tmp"]

config = {}
with open(resolve_file_local("config.json"), "r") as file:
    config = json.load(file)

llvm_root = os.path.realpath(config["llvm_root"])
flang_path = os.path.join(llvm_root, "build", "bin", "flang-new")
feature_plugin = os.path.join(llvm_root, "build", "lib", "flangFeatureList.so")

test_prefix = os.path.join(llvm_root, config.get("source_folder", "llvm-project"), "flang", "test")
fortran_files = [file for file in sys.argv[1:] if any(map(file.endswith, suffixes))]

if fortran_files:
    tmp_files = [file for file in fortran_files if ".tmp" in file]
    file = tmp_files[0] if tmp_files else fortran_files[0]
    test_name = normalize_test_name(file)
    
    plugin_args = [flang_path, "-fc1", "-fopenacc", "-fopenmp", "-load", feature_plugin, "-plugin", "feature-list", file]
    plugin_process = subprocess.run(plugin_args, capture_output=True)
    log_errors(("RUNNING" if plugin_process.returncode == 0 else "SKIPPING") + " TEST: " + file)

    if plugin_process.returncode > 0:
        sys.exit()
    stdout = plugin_process.stdout.decode()

    frequencies = {}
    for match in re.finditer(r"([:\w]+)\: (\d+)", stdout):
        frequencies[match.group(1)] = int(match.group(2))

    if not frequencies:
        log_errors("Skipping " + file + " (blank program)")
        sys.exit()
    
    flang_test_args = [flang_path]

    flang_test_args.extend(select_options(sys.argv[1:], param_opt))
    for opt in filter(lambda o: o in include_opt, sys.argv[1:]):
        flang_test_args.append(opt)
    
    flang_test_args.append("-c")
    flang_test_args.append(file)

    log_errors("Running " + str(flang_test_args))
    flang_process = subprocess.run(flang_test_args, capture_output=True)
    print(flang_process)
    compiled = flang_process.returncode == 0
    stderr = flang_process.stderr.decode()

    todo_match = re.search(r"not yet implemented: ([\w\(\)= \/\.\-\:]+)", stderr)
    todo_message = todo_match.group(1).strip() if todo_match else None

    if todo_message:
        log_errors("TODO found: " + str(todo_message) + " in file " + file)

    with sqlite3.connect(resolve_file_local("database.db")) as con:
        check_res = con.execute("SELECT id, name FROM test_file WHERE name = ?", (test_name,))
        if check_res.fetchone() is not None:
            log_errors("Skipping " + file)
            sys.exit()

        ins_test = con.execute("INSERT INTO test_file (name, can_compile) VALUES (?, ?)", (test_name, compiled))
        test_id = ins_test.lastrowid

        test_rows = []
        for name, frequency in frequencies.items():
            res = con.execute("SELECT id FROM tree_node WHERE name = ?", (name,))
            row = res.fetchone()
            test_rows.append((row[0], test_id, frequency))

        con.executemany("INSERT INTO node_frequency (node_id, test_id, frequency) VALUES (?, ?, ?)", test_rows)
        if todo_message is not None:
            todo_id = gen_todo(con, todo_message)
            con.execute("INSERT INTO todo_instance (test_id, msg_id) VALUES (?, ?)", (test_id, todo_id))

        con.commit()
        log_errors("Completed " + file)
