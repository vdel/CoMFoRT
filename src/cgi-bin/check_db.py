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

from conf import confstatic
from modules import module_interfaces

def check(db,mm):
  """
    Vérifie l'état de la table contenant les pages du site.
    En cas de nouveau module, met automatiquement la table à jour.
  """
  ##Checks pages:
  #Vérifie les pages:
  try:
    table=db.table(confstatic.pages_database_prefix)
    pages=table.select(cond = [])
    fields=table.GetScheme()
    missing=[]
    modules=filter(lambda m: isinstance(mm[m], module_interfaces.IModuleContentProvider), mm.get_available_modules())
    degenerate=False
    for m in modules:
      if not fields.has_key(m+"_priority"):
        fields[m+"_priority"]="integer"
        missing.append(m+"_priority")
        degenerate=True
    if degenerate:
      db.drop(confstatic.pages_database_prefix)
      db.create(confstatic.pages_database_prefix,fields)
      table=db.table(confstatic.pages_database_prefix)
      for p in pages:
        for i in missing:
          p[i]=-1
        table.insert(p)
  except:
    def create_page(name,wiki,created=[False]):
      fields={"page_id"    : "varchar",
              "page_title" : "varchar",
              "page_style" : "varchar",
              "page_wiki"  : "text" }
      new_page={"page_id"   : name,
                "page_title": _("Mon site perso"),
                "page_wiki" : wiki }
      modules=filter(lambda m: isinstance(mm[m], module_interfaces.IModuleContentProvider), mm.get_available_modules())
      for m in modules:
        fields[m+"_priority"]="integer"
        new_page[m+"_priority"]=-1
      
      priority=0
      for m in confstatic.default_active_modules:
        new_page[m+"_priority"]=priority
        priority += 1

      if not created[0]:
        db.create(confstatic.pages_database_prefix,fields);
        created[0] = True

      table=db.table(confstatic.pages_database_prefix)
      table.insert(new_page)
    
    create_page(confstatic.default_page_name, confstatic.default_page_wiki)
    create_page(confstatic.wikisyntax_page_name, confstatic.wikisyntax_page_wiki)
