#!/bin/sh
cd /root/Python/Azurite

#git remote add Azurite-Framework git@github.com:Red-C0der/Azurite-Framework.git

old="$IFS"
IFS=' '
str="'$*'"
commitmsg="$str"
IFS=$old

git add -A
git commit -a
git push -f git@github.com:Red-C0der/Azurite-Framework.git master
