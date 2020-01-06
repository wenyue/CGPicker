#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser

iniFileUrl = 'config.ini'
conf = configparser.ConfigParser()
conf.read(iniFileUrl, encoding='utf-8')


def set(*args, **kwargs):
	conf.set(*args, **kwargs)
	conf.write(open(iniFileUrl, 'w', encoding='utf-8'))


def get(*args, **kwargs):
	return conf.get(*args, **kwargs)
