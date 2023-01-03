#!/bin/bash
clear
rm -rf .git
git init
git config --global user.name "hoanghd"
git config --global user.email "hoanghd164@gmail.com"
git add .
git commit -m "The first commit"

if [[ $(git remote | grep -Eoc 'infra') == 0 ]];then git remote add infra git@gitlab.com:hoanghd164/infra.git;fi
git push -u --force infra master

if [[ $(git remote | grep -Eoc 'kustomize-demo') == 0 ]];then git remote add kustomize-demo https://github.com/hoanghd164/kustomize-demo.git;fi
git push -u --force kustomize-demo master