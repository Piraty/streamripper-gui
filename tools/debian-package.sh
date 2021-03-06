#!/bin/bash
which dpkg-deb
if [ $? != 0 ]; then
	echo "Error: dpkg-deb is missing!  You need to install dpkg."
	exit 1
fi

DIR="$(pwd)"
PWD="$(cd ${0%/*}/;pwd)"

PACKAGE=$1
VERSION=$2 #версия на пакета - задължително
DESCRIPTION="Simple and easy to use graphical frontend for streamripper" #описание на пакета - задължително
SECTION="USU Packages" #категория на пакета - може да не се пипа
PRIORITY="optional" #приоритет - може да не се пипа
MAINTAINER="$3 <$4>" #автор
DEPENDS="python, python-glade2, streamripper, python-dbus" #зависимости. имена на пакети отделени със запетайка и интервал: пакет1, пакет2, пакет3
INSTALEDSIZE_BYTES=`du --apparent-size -bs $PWD/../build/debian/ | cut -f1`
INSTALEDSIZE=$(($INSTALEDSIZE_BYTES/1024))
ARCHITECTURE="all"
# надолу нищо не се редактира
mkdir -p $PWD/../build/debian/DEBIAN/
echo "Package: $PACKAGE" > $PWD/../build/debian/DEBIAN/control
echo "Version: $VERSION" >> $PWD/../build/debian/DEBIAN/control
echo "Section: $SECTION" >> $PWD/../build/debian/DEBIAN/control
echo "Priority: $PRIORITY" >> $PWD/../build/debian/DEBIAN/control
echo "Architecture: $ARCHITECTURE" >> $PWD/../build/debian/DEBIAN/control
echo "Depends: $DEPENDS" >> $PWD/../build/debian/DEBIAN/control
echo "Maintainer: $MAINTAINER" >> $PWD/../build/debian/DEBIAN/control
echo "Description: $DESCRIPTION" >> $PWD/../build/debian/DEBIAN/control
echo "Installed-size: $INSTALEDSIZE" >> $PWD/../build/debian/DEBIAN/control

sudo chown -R root:root $PWD/../build/debian
sudo chmod -R 755 $PWD/../build/debian
[ -d $PWD/../dist ] || mkdir -p $PWD/../dist
sudo dpkg-deb --build $PWD/../build/debian $PWD/../dist/$PACKAGE-$VERSION-$ARCHITECTURE.deb
sudo chown -R $USER:$USER $PWD/../build/debian
cd $DIR
