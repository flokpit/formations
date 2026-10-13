#!/bin/sh
# Build the reproducible contract archive and its checksum file.
#
# Usage: scripts/build-archive.sh <path/to/archive.tar.gz>
#
# Contents are the contract (docs/decisions/001-contract-delivery-to-flokpit.md,
# decision 1): breeds/, formations/, specs/ and scripts/validate.py, at exactly
# those paths. validate.py derives its root from its own location, so the
# extracted tree validates in place; scripts/ is listed file by file because
# the rest of scripts/ is not part of the contract.
#
# Reproducible: sorted entries, fixed owner, mtime of HEAD, no gzip timestamp.
# Two builds of the same commit give the same sha256.
set -eu

archive=${1:?usage: build-archive.sh <path/to/archive.tar.gz>}

tar --sort=name --owner=0 --group=0 --numeric-owner \
    --mtime="@$(git log -1 --format=%ct)" \
    -cf - breeds formations specs scripts/validate.py | gzip -n -9 > "$archive"

# Checksum file with a bare file name, so `sha256sum -c` works next to it.
dir=$(dirname "$archive")
base=$(basename "$archive")
( cd "$dir" && sha256sum "$base" > "$base.sha256" )

tar -tzf "$archive"
cat "$archive.sha256"
