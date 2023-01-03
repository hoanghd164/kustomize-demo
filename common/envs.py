#!/usr/bin/env python3
import os, sys, re, ast, json, time, socket, random, subprocess, paramiko, requests, shutil
from sys import argv
from datetime import datetime
from jsonpath_ng import parse
from urllib.request import urlopen
from multiprocessing import Process

output = False