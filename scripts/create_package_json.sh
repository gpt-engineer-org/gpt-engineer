#!/bin/bash
npm init -y
for dep in $@; do
  npm install $dep
done

