#!/bin/bash -e

# Setup environment for building inside Dockerized toolchain
[ $(id -u) = 0 ] && umask 0

version=$(grep '"version"' manifest.json | cut -d: -f2 | cut -d\" -f2)

if [ -z "${ADDON_ARCH}" ]; then
    TARFILE_SUFFIX=
else
    PYTHON_VERSION="$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d. -f 1-2)"
    TARFILE_SUFFIX="-${ADDON_ARCH}-v${PYTHON_VERSION}"
fi

# Clean up from previous releases
rm -rf *.tgz package SHA256SUMS lib

# Prep new package
mkdir lib package

# Pull down Python dependencies.
#
# For 3.7/3.8 we additionally apply constraints-py-legacy.txt to keep
# transitive deps like cryptography on versions that still publish
# cp37/cp38 wheels for all architectures we target (notably armv7).
if [ "$PYTHON_VERSION" = "3.7" ] || [ "$PYTHON_VERSION" = "3.8" ]; then
pip3 install -r requirements.txt -c constraints-py-legacy.txt -t lib --prefix ""
else
pip3 install -r requirements.txt -t lib --no-binary :all: --prefix ""
fi

# Put package together
#cp -r lib pkg LICENSE README.md package.json manifest.json *.py package/
cp -r lib pkg LICENSE manifest.json package.json *.py README.md package/
find package -type f -name '*.pyc' -delete
find package -type d -empty -delete

# Generate checksums
cd package
sha256sum *.py pkg/*.py *.json README.md LICENSE > SHA256SUMS
find lib -type f -exec sha256sum {} \; >> SHA256SUMS
cd -

# Make the tarball
TARFILE="konnected-adapter-${version}${TARFILE_SUFFIX}.tgz"
tar czf ${TARFILE} package

shasum --algorithm 256 ${TARFILE} > ${TARFILE}.sha256sum

rm -rf SHA256SUMS package
