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
import os, os.path
import sys
import urllib
import htmlentitydefs

import confstatic
try:
  import conf_general
except:
  pass

def import_gettext():
  """Initialise gettext avec les fichiers PO définis dans confstatic"""
  import gettext
  gettext.bindtextdomain(confstatic.gettext_domain, confstatic.gettext_localedir)
  gettext.textdomain(confstatic.gettext_domain)
  gettext.install(confstatic.gettext_domain, confstatic.gettext_localedir)

def init_cgi():
  """Fait tous les imports nécessaires pour le CGI, envoie les headers, et fait
  une redirection si jamais confort n'est pas installé"""
  import cgitb
  cgitb.enable()

  print "Content-type: text/html"
  print

def redir(page):
    print """
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Index de CoMFoRT</title>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
  <meta http-equiv="Refresh" content="0;url=%s" />
</head>
<body style="margin: 1em;">
""" % page +_("Si vous n'êtes pas redirigé, cliquez <a href=\"%s\">ici</a>.") % page +"""
</body>
</html>"""

def error_page(msg):
    print """
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Index de CoMFoRT</title>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
</head>
<body style="margin: 1em;">
<pre>
%s
</pre>
</body>
</html>""" % msg

def check_installed():
  """Fait une redirection sur admin.py?id=install si jamais on n'a pas encore
  fait l'initialisation de CoMFoRT"""
  try:
    installed = conf_general.installed
  except:
    installed = 0    
  if installed == 0:
    redir("admin.py?id=install")
    sys.exit(0)

def select_mode():
  """Permet de mettre confstatic.mode à jour, avec deux valeurs possibles :
  - local : on est sur le mini serveur en Python
  - dynamic : on est sur un vrai serveur, genre Apache
  """
  try:
    if os.getenv("SERVER_SOFTWARE").startswith("SimpleHTTP"):
      confstatic.mode = "local"
    else:
      confstatic.mode = "dynamic"
  except AttributeError:
    confstatic.mode = "dynamic"

def parse_url(q_str):
  """Petite fonction utilitaire pour décoder les paramètres passés dans l'URL
  sous la forme d'un dictionnaire"""
  q_str=urllib.unquote(q_str)
  table={}
  try:
    params=q_str.split("&")
    for p in params:
      try:
        (key,value)=p.split("=")
        table[key]=value
      except:
        table[p]="" #il faut que la clé existe quand même
    return table    ##Key existence is still required
  except:
    return table

def java_ok():
  if os.name == "nt":
    return confstatic.nt_has_java
  else:
    dirs = os.getenv("PATH").split(":")
    for d in dirs:
      p = os.path.join(d, "java")
      if os.path.isfile(p):
        return True
    return False

def pdf_ok():
  if conf_general.pdfmode == "fop":
    return java_ok()
  elif conf_general.pdfmode == "latex":
    return os.path.isfile(confstatic.dblatex_path())
  elif conf_general.pdfmode == "none":
    return False

def latex_colors(chdir=None):
  """De quoi récupérer un couple contenant #123456,#123456 représentant les
  couleurs d'arrière-plan et d'avant-plan pour générer du latex. Renvoie blanc
  et noir sinon
  @param chdir: facultatif, si présent, on change au dossier en question pour
  être de nouveau dans src. La fonction retourne en revenant au dossier d'où
  elle a été appelée
  """
  cwd = os.getcwd()
  if chdir:
    os.chdir(chdir)
  try:
    f = open("styles/%s/latex.dat" % conf_general.style)
    bg = f.readline()[:-1]  ##to make the \n at end of line disappear
    fg = f.readline()[:-1]  #pour virer le \n en fin de chaîne
    f.close()
    os.chdir(cwd)
    return (bg,fg)
  except:
    os.chdir(cwd)
    return ("transparent","#000000")

def htmlentities(s):
  """Prend une chaîne en unicode (attention...) et la renvoie correctement
  échappée : faire donc utils.htmlentities(s.decode("utf-8"))"""
  ret = ""
  c2n = htmlentitydefs.codepoint2name
  for i in range(0, len(s)):
    n = ord(s[i])
    try:
      ret += "&" + c2n[n] + ";"
    except:
      ret += s[i]
  return ret

def mkdirp(dir):
  try:
    if dir != "" and not os.path.isdir(dir):
      p = os.path.dirname(dir)
      mkdirp(p)
      os.mkdir(dir)
  except:
    pass

def sanitize(s):
  s = s.replace("&", "&amp;")
  s = s.replace(">", "&gt;")
  s = s.replace("<", "&lt;")
  return s
