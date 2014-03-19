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

class ImplementationError(Exception):
  pass

class ComfortModule:
  
  position = ""
  mode = ""

  def __init__(self, mm):
    self.module_manager = mm

  def module_init(self):
    raise ImplementationError

  def module_title(self):
    raise ImplementationError

  def module_name(self):
    raise ImplementationError

  def setup_lang(self, l):
    self.lang = l

class IModuleAdminPage:
  def init_admin(self):
    raise ImplementationError
  def handle_admin_request(self, db, params, fields):
    raise ImplementationError
  def generate_admin_xhtml(self, page):
    raise ImplementationError
  def module_admin_info(self):
    raise ImplementationError    

class IModuleContentProvider:
  def init_content(self):
    raise ImplementationError
  def generate_content_xml(self, args):
    raise ImplementationError
  def module_id(self):
    raise ImplementationError

# servira pour une éventuelle version dynamique, si un module (imaginons
# commentaires) a besoin de connaître les formulaires envoyés sur sa page
class IModuleRequestHandler:
  def handle_request(self, request):
    raise ImplementationError

class IModuleDB:
  def setup_db(self, db):
    raise ImplementationError

# format à fixer
class IModuleRSS:
  def get_items(self):
    raise ImplementationError

# chaque module retourne une chaîne (human-readable) lorsqu'on lui demande
# d'exporter son contenu et chaque module prend pour importer une chaîne (la
# variable txt) et se débrouille avec
class IModuleImportExport:
  def doExport(self):
    raise ImplementationError
  def doImport(self, txt):
    raise ImplementationError
