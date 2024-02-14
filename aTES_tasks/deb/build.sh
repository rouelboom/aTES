#!/bin/sh

# INITIATION
NAME="task-tracker"
FILE_VERSION="$1"

if [ -z "$FILE_VERSION" ]; then
  # Should be replaced by git tag
  VERSION="1.0.0"
else
  VERSION=$FILE_VERSION
fi

SETUP_PATH="opt/algont/m7/pip-cache/$NAME"
ALEMBIC_PATH="/opt/algont/aTES/alembic/$NAME"

# FUNCTIONS
clear_tmp_folders()
{
  rm -rf ./deb/debinstall/$SETUP_PATH
  rm -rf ./deb/debinstall/var/log/aTES/$NAME
  rm -rf ./deb/debinstall/$ALEMBIC_PATH
}

# BODY
clear_tmp_folders

echo "Project name: $NAME"
echo "Version: $VERSION"
echo "START local build"

# create tmp folders
mkdir -pv ./deb/debinstall/$SETUP_PATH
mkdir -pv ./deb/debinstall/var/log/aTES/$NAME
mkdir -pv ./deb/debinstall/$ALEMBIC_PATH

# copy data
cp -r dist/* ./deb/debinstall/$SETUP_PATH
cp -r pip-cache/* ./deb/debinstall/$SETUP_PATH
cp -r alembic ./deb/debinstall/$ALEMBIC_PATH
cp -r alembic.ini ./deb/debinstall/$ALEMBIC_PATH

# add version to control
sed -i "/Version:/c\Version: $VERSION" ./deb/debinstall/DEBIAN/control

# build deb
fakeroot dpkg-deb --build ./deb/debinstall ./deb/$NAME"_""$VERSION""_all.deb" || exit 1
echo "FINISH local build"

# remove version from control
sed -i "/Version:/c\Version:" ./deb/debinstall/DEBIAN/control

clear_tmp_folders
