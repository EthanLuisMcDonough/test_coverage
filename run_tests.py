import json
import os
import stat
import subprocess
import sys

suffixes = [".f", ".F", ".ff", ".FOR", ".for", ".f77", ".f90", ".F90",
            ".ff90", ".f95", ".F95", ".ff95", ".fpp", ".FPP", ".cuf",
            ".CUF", ".f18", ".F18", ".f03", ".F03", ".f08", ".F08"]

def get_tests(test_dir):
    tests = []
    for (root, _, files) in os.walk(test_dir):
        for file in files:
            if any(map(file.endswith, suffixes)):
                tests.append(os.path.join(root, file))
    return tests

# Load configuration options
config = {}
with open("config.json", "r") as file:
    config = json.load(file)

llvm_root = os.path.realpath(config["llvm_root"])
llvm_lit = os.path.join("./", "build", "bin", "llvm-lit")

inserter_path = os.path.realpath("./insert_data.py")
os.chmod(inserter_path, os.stat(inserter_path).st_mode | stat.S_IEXEC)
replacement_flang = "flang-new=" + inserter_path
replacement_bbc = "bbc=" + inserter_path

test_dir = os.path.join(config.get("source_folder", "llvm-project"), "flang", "test")

test_paths = get_tests(os.path.join(llvm_root, test_dir))

for index, file_path in enumerate(test_paths, 1):
    print("[" + str(index) + " / " + str(len(test_paths)) + "] Running " + file_path, flush=True, end="\r")
    cmd_args = [llvm_lit, "-D", replacement_flang, "-D", replacement_bbc, os.path.join(llvm_root, test_dir, file_path)]
    subprocess.run(cmd_args, cwd=llvm_root, capture_output=True)
