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

from module_interfaces import *
from conf import confstatic
from interface import class_forms
import conf_general

class TheModule(ComfortModule, IModuleAdminPage):

  mode = "both"

  def module_init(self):
    pass

  def module_title(self):
    return _("Voir les contributeurs du projet")

  def module_name(self):
    return _("Crédits")

  def init_admin(self):
    pass

  def handle_admin_request(self, db, params, fields):
    return "handler.py"

  def module_admin_info(self):
    return _("Voir les contributeurs du projet")

  def generate_admin_xhtml(self, form_page):
    title = _("Crédits")
    form_page.page = class_forms.Page(title, conf_general.style)
    form_page.gen_nav()
    
    body = form_page.page.add_complex_option_tag("div", [("id", "credits")])
    credits = body.add_complex_option_tag("div", [("id", "cscroll")])
    credits.add_br()
    credits.add_br()
    credits.add_br()
    credits.add_text(_("Ont participé à ce projet, par ordre alphabétique :"))
    credits.add_br()
    credits.add_br()
    credits.add_br()
    gens = [
    "Jean-Alexandre Angles d'Auriac",
    "Gabriel Beaulieu",
    "Valentin Blot",
    "Pierre Boutillier",
    "Nicolas Brunie",
    "Aloïs Brunel",
    "Vincent Delaitre",
    "Antoine Frénoy",
    "Mathias Gaunard",
    "Guilhem Jaber",
    "Timo Jolivet",
    "Jonas Lefèvre",
    "Bastien Le Gloannec",
    "Anne-Laure Mouly",
    "Kevin Perrot",
    "Jonathan Protzenko",
    "Gabriel Renault",
    "Philippe Robert",
    "Pierre Roux",
    "Abdallah Saffidine",
    "David Salinas",
    "Félix Sipma",
    "Alexandra Sourisseau",
    "Samuel Vaiter",
    "Guillaume Vors"]
    for legens in gens:
      credits.add_text(legens)
      credits.add_br()
    form_page.gen_nav()

    form_page.page.add_text("""
<script type="text/javascript">
  var cscroll = document.getElementById("cscroll");
  var offset = 15;
  function doScroll() {
    offset -= 2;
    cscroll.style.marginTop = offset+"px";
    setTimeout(doScroll, 100);
  }
  setTimeout(doScroll, 1000);
</script>""")



