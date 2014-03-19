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


##This code is ugly but will be taken off before release version
#ce truc-là est moche, mais c'est uniquement pour la phase de développement
import sys
import os
sys.path.append(os.getcwd())
from conf import confstatic
sys.path = [confstatic.config_path]+sys.path
import conf_general, conf_private

##So that anybody can localise their strings
#pour que tout le monde puisse internationaliser ses chaînes
import gettext
gettext.bindtextdomain(confstatic.gettext_domain, confstatic.gettext_localedir)
gettext.textdomain(confstatic.gettext_domain)
gettext.install(confstatic.gettext_domain, confstatic.gettext_localedir)
lang = conf_general.language

def kill_server():
  """
  Kill the server.
  @return: nothing
  """
  file = open("server/running", 'w')
  file.write('0')
  file.close()

if __name__ == '__main__':
  kill_server()
  print "Content-type: text/html"
  print
  
  title=_("Arrêt du serveur")
  legend=_("Serveur arrêté")
  msg=_("Merci d'avoir utilisé CoMFoRT. Le serveur est désormais arrêté.")
  
  print ("""
      <!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">
      <html xmlns=\"http://www.w3.org/1999/xhtml\"> \n <head> \n <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
      <title>%s</title>
      <link rel="stylesheet" href="../styles/admin/%s" type="text/css"  media="screen"/>
      <link rel="shortcut icon" href="../styles/favicon.png" type="image/x-icon" />
      </head>
      <body>
      <div id="title">%s</div>
      <div class="body_class">
      <fieldset>
      <legend>%s</legend>
      <p>
      %s
      </p>
      </fieldset>
      </div>
      </body>
      </html>
""" %(title, conf_general.adminstyle, title, legend, msg))

