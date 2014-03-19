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
import os
os.chdir('..')

import gettext
gettext.install('comfort')
_ = gettext.lgettext
import module_manager
import module_interfaces


## Required step to use the module manager
#étape requise pour utiliser le gestionnaire de modules
mm = module_manager.ModuleManager()
mm2 = module_manager.ModuleManager()
print mm is mm2

print mm.get_available_modules()
print

## Preliminary to the modules loading
#préliminaire avant de commencer à charger des modules
mm.modules_mode = "dynamic"
print mm.modules_mode
## Protection: two modes, dynamic and local
#protection : deux modes, dynamic et local
try:
  mm.modules_mode = "3"
except module_manager.MMException, e:
  print e
print mm.modules_mode

## It is the way to load "dummy" module described in themodule_dummy.py
#c'est la façon de charger le module "dummy" codé dans themodule_dummy.py
mm[0] = "Dummy" ##Used as a Python dictionnary
                #utilisable comme dictionnaire python
## Module cannot be overwritten
#on ne peut pas écraser de module
try:
  mm['top_left'] = "other"
except module_manager.MMException, e:
  print e

print mm['top_left'] ## Prints class instance
                     #affiche l'instance de la classe
try:
  print mm['duh'] ## exception !
except module_manager.MMException, e:
  print e

##It is also an iterator
#c'est aussi un itérateur
print "Iterating over loaded modules"
for m in mm:
  print m, mm[m]

##Test on module capacities
#test sur les capacités du module
print isinstance(mm['top_left'],module_interfaces.IModuleContentProvider)
print isinstance(mm['top_left'],module_interfaces.IModuleAdminPage)

###### Testing module Publi ######
#### On teste le module Publi ####

mm['hey_dude'] = "Publi" 
## A few tests
# on fait quelques tests....
print mm['hey_dude'].module_info()

## One need the proper PYTHONPATH
# Il faut avoir le bon PYTHONPATH 
# import db_manager
# from conf import conf, conf_private
# from conf import confstatic
# db = db_manager.DBManager(conf.server_db)
# mm['hey_dude'].setup_db(db)
# mm['hey_dude'].parse_doc(' # @article{ACP1987,\n #  author    = {Stefan Arnborg and Derek G. Corneil and Andrzej Proskurowski},\n #  title     = {Complexity of Finding Embeddings in a $k$-Tree},\n #  journal   = JADM,\n\
#  pages     = {277-284},\n # year      = 1987,\n #  volume    = 8,\n #  number    = 2,\n #  note      = {\url{http://dx.doi.org/10.1137/0608024}},\n #  comment   = {alt url \url{http://link.aip.org/link/?SML/8/277/1}}\n #}\n #')
