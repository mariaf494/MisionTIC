#!/bin/sh

git pull origin main
supervisorctl restart misiontic
