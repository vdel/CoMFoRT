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


import shutil
import os, os.path
import sys
import shutil

from conf import confstatic
import conf_general, conf_private
from conf import utils
utils.import_gettext()


import check_db

## All the subparts that are to be gathered to generate the page
#toutes les sous-parties qu'il faut assembler entre elles pour générer la page
from modules import module_manager
from templates import template_manager

def generate_page(page,args,db):
  ## Module manager initialization
  #on initialise le gestionnaire de modules
  mm = module_manager.ModuleManager(set=[False])
  mm.modules_mode = confstatic.mode
  mm.forward_lang(conf_general.language)

  for module in mm.get_available_modules():
    mm[module]=module
    mm.forward_db_init(db)

  check_db.check(db,mm)
  
  ## Templates manager needs the database and the name of the asked page to
  ## guess which modules have to be activated
  #le gestionnaire de templates, qui a besoin de la base de données et du nom de
  #la page demandée pour déterminer quels modules activer
  
  args["page"] = page
  try:
    tm = template_manager.TemplateManager(db, page, args)
    tm.setup_modules(mm)
  except template_manager.TMException, e:
    print _("Error initializing templates engine : %s") % e.__str__()
    sys.exit(1)
  except Exception, e:
    print "Unexpected exception ", e
    print sys.exc_info()
  ## Link to the database forwarded to modules that require it
  #on fait suivre la connexion à la base de données aux modules qui en ont
  #besoin
  mm.forward_db_init(db)

  ## XHTML generation
  #et on génère le XHTML  
  x =  tm.generate_xhtml()

  fname = confstatic.build_url(args)
  f = open(os.path.join(confstatic.generate_path,fname), "w")  
  
  f.write(x)
  f.close()

  if utils.pdf_ok():
    args["pdf"] = "1"
    tm.generate_pdf(redir=False)


def generate_site(db):
  utils.mkdirp(confstatic.generate_path)
  print "<ul><li>"+_("Copie des fichiers latex, de style, ainsi que vos pages personnelles et vos images")+"</li>"
  ## Updates the latex file (useful for pdf files)
  #met à jour le latex (utile pour les pdf)
  try:
    shutil.rmtree(os.path.join(confstatic.generate_path,"latex"))
    shutil.copytree(confstatic.latex_path, os.path.join(confstatic.generate_path,"latex"))
  except OSError:
    pass
  ## Updates the style
  #met à jour le style
  try:
    utils.mkdirp(os.path.join(confstatic.generate_path,"styles"))
    shutil.copytree(os.path.join("styles",conf_general.style), os.path.join(confstatic.generate_path,"styles",conf_general.style))
  except OSError:
    pass
  ## Updates common
  #met à jour common  
  try:
    shutil.copytree(os.path.join("styles","common"), os.path.join(confstatic.generate_path,"styles","common"))
  except OSError:
    pass
  ## Updates personal page
  #met à jour le perso
  try:
    shutil.rmtree(os.path.join(confstatic.generate_path,"perso"))
    shutil.copytree(os.path.join(confstatic.config_path,"perso"), os.path.join(confstatic.generate_path,"perso"))
  except OSError:
    pass
 
    
  confstatic.generating = True
  confstatic.build_url = confstatic.build_url_for_generation  
  tpages = db.table(confstatic.pages_database_prefix)
  pages = tpages.select()
  last_cwd = os.getcwd()
  try:
    while True:
      p = pages.next()
      print "<li>"+((_("Génération de la page %s: ")+"\"%s\"") % (p["page_id"],p["page_title"]))+"</li>"
      sys.stdout.flush()
      generate_page(p["page_id"], {}, db)
  except StopIteration:
    os.chdir(last_cwd)
  
  shutil.copy(os.path.join(confstatic.generate_path,confstatic.build_url({"page":confstatic.default_page_name+".html"})), os.path.join(confstatic.generate_path,"index.html"))
  shutil.copy(os.path.join(confstatic.generate_path,confstatic.build_url({"page":confstatic.default_page_name+".html"})), os.path.join(confstatic.generate_path,"index.htm"))
  
  shutil.copy(os.path.join("styles","favicon.png"), os.path.join(confstatic.generate_path,"styles","favicon.png"))
  shutil.copy(os.path.join("styles","comfort_thumb.png"), os.path.join(confstatic.generate_path,"styles","comfort_thumb.png"))
  shutil.copy(os.path.join(confstatic.config_path,"database"), os.path.join(confstatic.generate_path,".database"))
  shutil.copy(os.path.join(confstatic.config_path,"conf_general.py"), os.path.join(confstatic.generate_path,".conf_general.py"))

  print "</ul>"
  
def clean():
  ## Upgrades the latex file
  #met à jour le latex
  try:
    shutil.rmtree(os.path.join(confstatic.latex_path))
    shutil.copytree(os.path.join(confstatic.generate_path,"latex"), confstatic.latex_path)
  except OSError:
    pass


  ## Upgrades the personal page
  #met à jour le perso
  try:
    shutil.rmtree(os.path.join(confstatic.config_path,"perso"))
    shutil.copytree(os.path.join(confstatic.generate_path,"perso"), os.path.join(confstatic.config_path,"perso"))
  except OSError:
    pass    


  shutil.copy(os.path.join(confstatic.generate_path,".database"), os.path.join(confstatic.config_path,"database"))
  shutil.copy(os.path.join(confstatic.generate_path,".conf_general.py"), os.path.join(confstatic.config_path,"conf_general.py"))
  
  confstatic.generating = False   
  confstatic.build_url = confstatic.build_url_standard 
