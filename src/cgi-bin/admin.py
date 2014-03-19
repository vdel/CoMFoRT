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

import cgi

import sys
import os
p = os.getenv("COMFORTPATH")
if p != None:
  os.chdir(p)
sys.path.append(os.getcwd())

from conf import confstatic
sys.path = [confstatic.config_path]+sys.path
import conf_general, conf_private
from conf import utils

import check_db

##Databases, formularies and modules handling
#pour les modules, la base de données et les formulaires
from db import db_manager
from modules import module_manager
from interface import class_forms
from interface import forms

fields= cgi.FieldStorage(keep_blank_values=1)
try:
  params = utils.parse_url(os.getenv("QUERY_STRING"))
except:
  params = utils.parse_url("")

utils.import_gettext()
utils.init_cgi()
utils.select_mode()
confstatic.build_url = confstatic.build_url_standard 

##Module handling initialization
#on initialise le gestionnaire de modules
mm = module_manager.ModuleManager()
mm.modules_mode = confstatic.mode
mm.forward_lang(conf_general.language)

##Database initialization
#on initialise la base de données
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

forms.Formulaire(mm,db.instance,params,fields).generate()
