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
#! /usr/bin/python


## IMPORTS ORDER
## 1) What is provided by Python librairies, and firstly what is used for the 
##    path
## 2) What is linked to configuring CoMFoRT
## 3) Modules, database, templates
# ORDRE DES IMPORTS :
# 1) ce qui est dans la lib standard python, avec en premier ce qui sert pour le
#   path
# 2) ce qui est de l'ordre de la configuration de comfort 
# 3) modules, db, templates

import sys
import os
p = os.getenv("COMFORTPATH")
if p != None:
  os.chdir(p)
sys.path.append(os.getcwd())

import cgi
import urllib

from conf import confstatic
sys.path = [confstatic.config_path]+sys.path

from conf import utils

try:
  import conf_general
  import conf_private
except:
  for d in [confstatic.config_path, confstatic.perso_path, confstatic.pages_path, confstatic.docs_path, ]:
    utils.mkdirp(d)
  open(os.path.join(confstatic.config_path, '__init__.py'), 'w').close()

  fconf = open(os.path.join(confstatic.config_path, "conf_general.py"), 'w+')
  fconf.write("# -*- encoding: utf-8 -*-\n\n#ATTENTION : Ce fichier est genere par interface/valid_form.py\n\n")
  fconf.write("title = \"\"\n")
  fconf.write("language = \"\"\n")
  fconf.write("style = \"officiels_serious\"\n")
  fconf.write("\n")
  fconf.write("installed = 0\n")
  fconf.write("pdfmode = \"none\"\n")
  fconf.write("adminstyle = \"admin2.css\"\n")
  fconf.write("display_logo = 0\n")
  fconf.close()

  fconf = open(os.path.join(confstatic.config_path, "conf_private.py"), 'w+')
  fconf.write("# -*- encoding: utf-8 -*-\n\n#ATTENTION : Ce fichier est genere par interface/valid_form.py\n\n")
  fconf.write("transfer_mode = \"FTP\"\n")
  fconf.write("\n")
  fconf.write("server_ftp = \"\"\n")
  fconf.write("user_ftp = \"\"\n")
  fconf.write("pass_ftp = \"\"\n")
  fconf.write("root_ftp = \"\"\n")
  fconf.write("\n")
  fconf.write("server_ssh = \"\"\n")
  fconf.close()


utils.init_cgi()
utils.import_gettext()
utils.check_installed()

import check_db

## All the subparts that are to be gathered to generate the page
#toutes les sous-parties qu'il faut assembler entre elles pour générer la page
from modules import module_manager
from db import db_manager
from templates import template_manager

try:
  args = utils.parse_url(os.getenv("QUERY_STRING"))
except:
  args = utils.parse_url("")

try:
  page = args["page"]
  page = page[:page.rindex(".")]
except:
  page = confstatic.default_page_name
  args["page"] = page+".html"


utils.select_mode()
confstatic.build_url = confstatic.build_url_standard 

##Modules manager initialization
#on initialise le gestionnaire de modules
mm = module_manager.ModuleManager()
mm.modules_mode = confstatic.mode
mm.forward_lang(conf_general.language)

##Database initialization
#puis la base de données
try:
  db = db_manager.DBManager(None)
except db_manager.DBException, e:
  print _("Erreur d'initialisation de la base de données : %s") % e.__str__()
  sys.exit(1)

## we load all modules
## check_db checks that the DB contains
## all information concerning the ContentProvider modules
# on charge tous les modules
# check_db vérifie que la BDD contient les
# informations relatives aux modules générateurs de contenu

for module in mm.get_available_modules():
  mm[module]=module
  mm.forward_db_init(db.instance)
  
check_db.check(db.instance,mm)

##Checks wether asked page exists
#Vérifie que la page demandée existe
try:
  db.instance.table(confstatic.pages_database_prefix).select(cond=[("page_id","=",page)]).next()
except:
  page = confstatic.default_page_name
  args["page"] = page+".html"

## Templates manager that needs the database and the name of the wanted page to
## specify which modules to activate
#le gestionnaire de templates, qui a besoin de la base de données et du nom de
#la page demandée pour déterminer quels modules activer
try:
  tm = template_manager.TemplateManager(db.instance, urllib.unquote(page), args)
  tm.setup_modules(mm)
except template_manager.TMException, e:
  print _("Erreur d'initialisation du moteur de templates : %s") % e.__str__()
  sys.exit(1)

## Forwards link to databade to modules that need it
#on fait suivre la connexion à la base de données aux modules qui en ont besoin
mm.forward_db_init(db.instance)

## XHTML is generated
#et on génère le XHTML
try:
  if args["pdf"] == "1":
    confstatic.mode = "local"
    confstatic.build_url = confstatic.build_url_for_generation
    confstatic.files_url = "../"
    confstatic.pictures_url = confstatic.files_url+"pictures/"
    confstatic.pages_url = confstatic.files_url+"pages/"    
    confstatic.doc_url = confstatic.files_url+"docs/"
    if utils.pdf_ok():
      tm.generate_pdf()
    else:
      print _("Vous n'avez pas FOP d'installé : veuillez vous référer au guide d'installation pour apprendre à générer des fichiers PDF")
  else:
    print tm.generate_xhtml()
except KeyError:
  print tm.generate_xhtml()
