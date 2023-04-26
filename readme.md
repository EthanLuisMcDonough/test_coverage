# Flang node test coverage tool

## Building flang with extensions

This coverage test requires flang to be built with examples enabled.  You can build the project with the following script:

```shell
rm -rf build # clean any existing build
mkdir build
mkdir install
git clone --single-branch --depth 1 https://github.com/llvm/llvm-project.git
ROOTDIR=`pwd`
INSTALLDIR=$ROOTDIR/install
cd build
cmake \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=$INSTALLDIR \
        -DCMAKE_CXX_STANDARD=17 \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
        -DCMAKE_CXX_LINK_FLAGS="-Wl,-rpath,$LD_LIBRARY_PATH" \
        -DFLANG_ENABLE_WERROR=ON \
        -DLLVM_ENABLE_ASSERTIONS=ON \
        -DLLVM_TARGETS_TO_BUILD=host \
        -DLLVM_BUILD_EXAMPLES=ON \
        -DLLVM_LIT_ARGS=-v \
        -DLIBOMPTARGET_ENABLE_DEBUG=1 \
        -DLLVM_ENABLE_PROJECTS="clang;mlir;flang" \
        -DLLVM_ENABLE_RUNTIMES="compiler-rt;openmp" \
        ../llvm-project/llvm

ninja
ninja install

echo "Your config file: { \"llvm_root:\": \"$ROOTDIR\" }"
```

## Running Test Coverage

Requires SQLite (min ver 3.31.1) and Python 3 (min ver 3.8.10). 

1. `git clone https://github.com/EthanLuisMcDonough/test_coverage`
2. `cd test_coverage`
3. `sqlite3 database.db<db.schema`
4. Create a file named `config.json` and set ìts contents to `{ "llvm_root": "YOUR_FLANG_PATH" }`.  If you built using the instructions in part 1, this will be JSON that comes after `"Your config file: "`.
5. `python3 run_tests.py`
6. `sqlite database.db`
7. Query gathered data.  Some examples can be found in `sample_queries.sql`.  Just paste a query into console and hit enter.
