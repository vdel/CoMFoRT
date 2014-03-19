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
from UserDict import *
import module_interfaces
import os


modes = ['dynamic', 'local', 'both']

## Some explanations:
##  To use ModuleManager, one create an instance of ModuleManager, then choses
##  the module that will be placed on that position like this:
##  mm = module_manager.ModuleManager()
##  mm[0] = 'dummy' 
##  The MM will then instanciate the class TheModule stocked in the file
##  themodule_dummy.py (standard convention) located in its folder. As the
##  interfaces are standard, blah, blah, blah
# Quelques explications :
#  On utilise le ModuleManager en en créant une instance, puis en choisissant le
#  module qui sera à telle position de la façon suivante :
#  mm = module_manager.ModuleManager()
#  mm[0] = 'dummy'
#  Le MM va ensuite instancier la classe TheModule stockée dans le fichier
#  themodule_dummy.py (convention standard) située dans son dossier. Comme les
#  interfaces sont standard, blah, blah, blah


class MMException(Exception):
  pass


class _ModuleManager(object, IterableUserDict):

  def __init__(self):
    self.__modules_mode = None
    self.page = ""  ##initialized by the template manager
                    #initialisé par le template_manager
    IterableUserDict.__init__(self)
  
  def get_mm(self):
    return self.__modules_mode

  def set_mm(self, mm):
    if self.__modules_mode is not None:
      raise MMException(_("les propriétés de modules_mode sont déjà définies"))
    if mm not in modes:
      raise MMException(_("mode inconnu"))
    else:
      self.__modules_mode = mm

  modules_mode = property(get_mm, set_mm)

  def __getitem__(self, key):
    if key in self:
      return IterableUserDict.__getitem__(self, key)
    else:
      raise MMException(_("pas de module à la clé %s") % key)

  def __setitem__(self, key, val):
    if key in self:
      raise MMException(_("il y a déjà un module à la position %s") % key)
      #IterableUserDict.__getitem__(self,key).__class__.__name__  
    elif self.__modules_mode is None:
      raise MMException(_("vous devez avant tout définir un mode"))
    else:
      instance = None
      code = "import themodule_"+val+"\n"
      code += "instance = themodule_"+val+".TheModule(self)"
      try:
        exec(code)
      except ImportError:
        raise MMException(_("Module inconnu : %s") % val)

      if instance.mode != self.__modules_mode and instance.mode != 'both':
        raise MMException((_("Le mode courant est %s ;") % self.__modules_mode)+(_(" ce mode de module est %s - incompatible") % instance.mode))
      else:
        instance.position = key
        instance.module_init()

        IterableUserDict.__setitem__(self,key,instance)

  def forward_db_init(self, db):
    """Simple db initialisation function.
    @param db: the database instance that is forwarded to every module
    @type db: DBManager
    """
    for key in self:
      m = IterableUserDict.__getitem__(self, key)
      if isinstance(m, module_interfaces.IModuleDB):
        m.setup_db(db)

  def forward_lang(self, l):
    """Same as forward_db_init for the lang.
    @param l: the current lang used in the CMS
    @type l: string
    """
    for key in self:
      m = IterableUserDict.__getitem__(self, key)
      m.setup_lang(l)

  def get_available_modules():
    """Returns a list of available modules (based on the directory listing).
    This is a good example of pythonic programming style
    @return: a list of available modules.
    """
    l = os.listdir("modules")
    l = filter(lambda f: f.startswith("themodule_") and f.endswith('.py'), l[:])
    return [f.split('_')[1][:-3] for f in l]

  get_available_modules = staticmethod(get_available_modules)


def ModuleManager(set=[False], instance=[None]):
  """That function tries to implement the singleton pattern : there is one and
  only one instance of _ModuleManager per run of the program. Actually, this
  behaviour is overridden in:
  - interface/forms.py when the menu is loaded
  - interface/generate.py when different pages are generated
  - modules/themoduleWiki.py when the content of a <module> tag is generated.
  (there is a new instance of _ModuleManager created per page)."""
  if not set[0]:
    instance[0] = _ModuleManager()
    set[0] = True
  return instance[0]
