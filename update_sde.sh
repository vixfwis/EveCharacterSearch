#!/bin/bash

archive="sqlite-latest.sqlite.bz2"
db="sqlite-latest.sqlite"
sde="eve-sde.sqlite"

download_db() {
    wget -O $archive https://www.fuzzwork.co.uk/dump/$archive
    echo "Decompressing"
    bzip2 -dk $archive
    mv $db $sde
}

if [[ -e "$archive" ]]; then
    wget -O $archive.md5 https://www.fuzzwork.co.uk/dump/$archive.md5
    if !(md5sum -c $archive.md5); then
        download_db
    fi
else
    download_db
fi
echo "Done!"
