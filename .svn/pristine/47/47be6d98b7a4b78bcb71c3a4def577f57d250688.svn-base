#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# CoMFoRT: a COntent Management system FOr Researchers and Teachers!
# 
# Copyright (C) 2008 Projet2-L3IF ENS Lyon.
# 
# Contributors:
#    * Jean-Alexandre Angles d'Auriac
#    * Gabriel Beaulieu
#    * Valentin Blot
#    * Pierre Boutillier
#    * Nicolas Brunie
#    * Aloïs Brunel
#    * Vincent Delaitre
#    * Antoine Frénoy
#    * Mathias Gaunard
#    * Guilhem Jaber
#    * Timo Jolivet
#    * Jonas Lefèvre
#    * Bastien Le Gloannec
#    * Anne-Laure Mouly
#    * Kevin Perrot
#    * Jonathan Protzenko
#    * Gabriel Renault
#    * Philippe Robert
#    * Pierre Roux
#    * Abdallah Saffidine
#    * David Salinas
#    * Félix Sipma
#    * Alexandra Sourisseau
#    * Samuel Vaiter
#    * Guillaume Vors 
#
# Contact us with : comfort@listes.ens-lyon.fr
#
# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>."
#

import SimpleHTTPServer
import BaseHTTPServer
import CGIHTTPServer

import threading

import os, os.path

import time


def _launch_server(adress, port):
  """
  Just a simple local server.
  @param adress: the adress through which the server will be accessible
  @type adress: string
  @param port: the port through which the server will be accessible
  @type port: integer
  @return: nothing
  """
  try:
    HandlerClass = CGIHTTPServer.CGIHTTPRequestHandler
    HandlerClass.cgi_directories = ['/cgi-bin']
    ServerClass = BaseHTTPServer.HTTPServer
    server_address = (adress, port)
    HandlerClass.protocol_version = "HTTP/1.0"
    httpd = ServerClass(server_address, HandlerClass)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.setDaemon(True)
    thread.start()
  except:
    pass


def _keep_running():
  """
  Wait for server stop signal.
  """
  file = open('running', 'w')
  file.write('1')
  file.close()

  while 1:
    time.sleep(1)

    file = open('running', 'r')
    r = file.read()
    file.close()
    if r != '1':
      break


if __name__ == '__main__':
  import sys; sys.path.append('.');
  from conf import confstatic
  from conf import utils
  utils.mkdirp(confstatic.config_path)
  os.chdir(confstatic.config_path)
  sys.path.pop()
  _launch_server('', confstatic.get_user_server_port())
  _keep_running()
