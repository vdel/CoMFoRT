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

## Problems:
##  - How to cancel an import
##  - Order in the dates and international
##  - Protector erasement
##  - Separate past and future (+put some static deadlines)
##  - Database inconsitent
#pbs : 
#  - support datetime dans db_xml
#  - ordre dans les dates et internationnal 
#  - garde-fou effacement
#  - separer passé futur (+mettre des echeance en statique)
#  - incoherence db

from module_interfaces import *

from conf import confstatic
import conf_general, conf_private
from db import db_manager
from interface import class_forms
from vobject import base as vobject

class TheModule(ComfortModule, IModuleContentProvider, IModuleDB,  IModuleAdminPage):
  
  mode = "both"
  
  def form_date(self, date, prefix):
    """
    Permet de passer d'une date "date" au format bdd à un formulaire contenant les bon champs prefixé par "prefix"
    """
    aff = class_forms.Content("","")
    if date == "":
      aff.add_input_maxlength("text",prefix+"_d","",2)
      aff.add_text("/")
      aff.add_input_maxlength("text",prefix+"_m","",2)
      aff.add_text("/")
      aff.add_input_maxlength("text",prefix+"_y","20",4)
      aff.add_text("&nbsp;")
      aff.add_input_maxlength("text",prefix+"_h","00",2)
      aff.add_text(":")
      aff.add_input_maxlength("text",prefix+"_min","00",2)
    else:
      aff.add_input_maxlength("text",prefix+"_d",date[8:10],2)
      aff.add_text("/")
      aff.add_input_maxlength("text",prefix+"_m",date[5:7],2)
      aff.add_text("/")
      aff.add_input_maxlength("text",prefix+"_y",date[0:4],4)
      aff.add_text("&nbsp;")
      aff.add_input_maxlength("text",prefix+"_h",date[11:13],2)
      aff.add_text(":")
      aff.add_input_maxlength("text",prefix+"_min",date[14:16],2)
    return aff

  def parse_date(self,date):
    """
    Passe d'une date "date" au format bdd à une date francaise (!gettext peut il faire l'internationnalisation de cela ?)
    """
    str = date[8:10] + "/" + date[5:7] + "/" + date[0:4]
    if (date[11:13] != "00")|(date[14:16] != "00") :
      str += " " + date[11:13] + ":" + date[14:16]
    return str

  def conc_date(self, fields, prefix):
    """
    Fait de plein de champs de date de "fields" commancant par "prefix" une date au format bdd
    """
    if len(fields[prefix+"_y"].value) == 2:
      str = "20" + fields[prefix+"_y"].value
    else:
      str = fields[prefix+"_y"].value

    str += "-"

    if len(fields[prefix+"_m"].value) == 1:
      str += "0" + fields[prefix+"_m"].value
    else: 
      str += fields[prefix+"_m"].value
      
    str += "-" 

    if len(fields[prefix+"_d"].value) == 1:
      str += "0" + fields[prefix+"_d"].value
    else:
      str += fields[prefix+"_d"].value

    str += " "

    if len(fields[prefix+"_h"].value) == 1:
      str += "0" + fields[prefix+"_h"].value
    else:
      str += fields[prefix+"_h"].value 
    str += ":" 

    if len(fields[prefix+"_min"].value) == 1:
      str += "0" + fields[prefix+"_min"].value
    else:
      str += fields[prefix+"_min"].value 
    str += ":00" 
    return str

  def module_init(self):
    self.table_prefix="calendars"

  def module_admin_info(self):
    return _("Permet de gérer les événements publics à venir de votre agenda.")
    
  def module_title(self):
    return _("Événements à venir")

  def module_name(self):
    return _("Calendrier")

  def module_id(self):
    return "Calendrier"

  def init_content(self):
    pass

  def generate_content_xml(self, args):

    nonempty = False
    str = "<variablelist>"
    for it in self.db.table(self.table_prefix+"_items").select(order=[("begin",True)]):
      str += "<varlistentry>"
      str += "<term>" + self.parse_date(it["begin"]) + "</term>"
      if (it["begin"]!=it["end"]):
        str += "<term>" + self.parse_date(it["end"]) + "</term>"
      str +=  "<listitem>" + it["text"] + "</listitem>"
      str += "</varlistentry>"
      nonempty = True
    str += "</variablelist>"

    if nonempty:
      return str
    else:
      return ""

  def setup_db(self, db):
    self.db = db
    try:
      self.db.table(self.table_prefix+"_items")
    except:
      self.db.create(self.table_prefix+"_items", {"text" :"varchar","begin" :"datetime", "end":"datetime"});

  def handle_admin_request(self, params, fields):
    if params["action"] == "add":
      self.db.table(self.table_prefix+"_items").insert(
        {'begin' : self.conc_date(fields,"begin"), 'end' : self.conc_date(fields,"end"), 'text' : fields['item_text'].value})
      return "admin.py?id=Calendars"
    elif params["action"] == "del":
      self.db.table(self.table_prefix+"_items").delete([("id", "=", params["item_id"])])
      return "admin.py?id=Calendars"
    elif params["action"] == "update":
      self.db.table(self.table_prefix+"_items").update({ 'id' : params["item_id"], 'begin' : self.conc_date(fields,"begin"), 'end' : self.conc_date(fields,"end"), 'text' : fields['item_text'].value}, [("id", "=", params["item_id"])])
    elif params["action"] == "import":
      try:
        self.db.drop(self.table_prefix+"_temp")
      except:
        pass
      self.db.create(self.table_prefix+"_temp", {"text" :"varchar","begin" :"datetime", "end":"datetime"});
      fcal = vobject.readOne(fields['cal'].file.read()).vevent_list
      for fev in fcal:
        self.db.table(self.table_prefix+"_temp").insert({'begin' : fev.dtstart.value ,
                                                         'end' : fev.dtend.value ,
                                                         'text' : fev.summary.value })
      return "admin.py?id=Calendars&amp;action=choose"
    elif params["action"] == "include":
      for i in range(int(fields["nb_it"].value)):
        if fields.has_key("check_"+str(i)):
          self.db.table(self.table_prefix+"_items").insert(
            {'begin' : fields["begin_"+str(i)].value, 'end' : fields["end_"+str(i)].value, 'text' : fields['text_'+str(i)].value})
      return "admin.py?id=Calendars"
    else:
      return "admin.py?id=Calendars"

  def generate_admin_xhtml(self, form_page):
    ## Headings
    #entete
    #self.db.drop("calendars_items")
    title=_("Gestion des événements")
    form_page.page = class_forms.Page(title,conf_general.style)
    title_content  = form_page.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    form_page.gen_nav()
    
    ## menu
    body = (form_page.page.add_complex_option_tag("div",[("class","body_class")]))
    menu = body.add_complex_tag("fieldset")
    menu.add_simple_tag("legend",_("Opérations sur les événements"))

    table_menu = menu.add_table(0,0,3)

    form_aff = class_forms.Content("","").add_form("admin.py","get")
    aff = form_aff.add_complex_tag("p")
    aff.add_input("hidden", "id", "Calendars")
    aff.add_input("submit", "",_("Liste actuelle"))

    form_import = class_forms.Content("","").add_form("admin.py","get")
    imp = form_import.add_complex_tag("p")
    imp.add_input("hidden", "id", "Calendars")
    imp.add_input("hidden","action", "import")
    imp.add_input("submit", "", _("Importer un calendrier ics")) 

#    form_options = class_forms.Content("","").add_form("admin.py","get")
#    op = form_options.add_complex_tag("p")
#    op.add_input("hidden", "id", "Calendars")
#    op.add_input("hidden","action", "options")
#    op.add_input("submit", "", _("Options")) 

    table_menu.add_line([("td", [], form_aff), ("td", [], form_import)])
    
    p = form_page.page.add_complex_tag("p")
    p.add_br()

    if form_page.params.has_key("action"):
      if form_page.params["action"] == "options":
        ## Options menu
        #menu d'options
        body = form_page.page.add_complex_option_tag("div",[("class","body_class")])
        aff_op = body.add_complex_tag("fieldset")
        aff_op.add_simple_tag("legend",_("Options d'affichage"))

        body.add_br()
        clean_op = body.add_complex_tag("fieldset")
        clean_op.add_simple_tag("legend",_("Opérations de maintenance"))
      elif form_page.params["action"] == "edit": 
        ## Entry editing menu
        #menu d'edition d'entree
        body = form_page.page.add_complex_option_tag("div",[("class","body_class")])
        items = (self.db.table(self.table_prefix+"_items")).select( cond=[("id","=",form_page.params["item_id"])])
        body.add_br()
        aff_ed = body.add_complex_tag("fieldset")
        aff_ed.add_simple_tag("legend",_("Édition d'un élément"))
        form_ed = aff_ed.add_form("adminvalid.py?id=Calendars&amp;action=update&amp;item_id=" +str(form_page.params["item_id"]),"post")
        table_ed = form_ed.add_table(0,0,5)
        for it in items:
          table_ed.add_line([("th",[],class_forms.Text(_("Début"))), ("td",[],self.form_date(it["begin"],"begin"))])
          table_ed.add_line([("th",[],class_forms.Text(_("Fin"))), ("td",[],self.form_date(it["end"],"end"))])
          table_ed.add_line([("th",[],class_forms.Text(_("Description"))), ("td",[],class_forms.Input_maxlength( "text","item_text",it["text"],30))])
        form_ed.add_complex_tag("div").add_input("submit", "submit", _("Modifier"))
        form_del = aff_ed.add_form( "adminvalid.py?id=Calendars&amp;action=del&amp;item_id="+str(form_page.params["item_id"]),"post")
        form_del.add_complex_tag("div").add_input("submit","submit",_("Effacer"))

        form = body.add_form("admin.py?id=Calendars", "post")
        p = form.add_complex_tag("p")      
        p.add_input("submit", "submit", _("Retour"))
      elif form_page.params["action"] == "import": 
        ## Import vcalendars menu
        #menu d'import vcalendars
        body.add_br()
        aff_imp = body.add_complex_tag("fieldset")
        aff_imp.add_simple_tag("legend",_("Import d'un fichier vcalendar"))
        form_imp = aff_imp.add_complex_option_tag("form",[("action","adminvalid.py?id=Calendars&amp;action=import"),("method","post"),("enctype","multipart/form-data")]) #"text/calendar"
        form_imp.add_labeled_input("file",_("Fichier à importer"),"cal","")
        form_imp.add_input("submit","submit",_("Importer"))
      elif form_page.params["action"] == "choose":
        ## Choose vcalendars' events to import
        #choix des evenements vcalendars à inserer
        body.add_br()
        aff_choo = body.add_complex_tag("fieldset")
        items = (self.db.table(self.table_prefix+"_temp")).select( order=[("begin",True)])
        aff_choo.add_simple_tag("legend",_("Choix des évènements à importer"))
        form_choo = aff_choo.add_form("adminvalid.py?id=Calendars&amp;action=include","post")
        table_item = form_choo.add_table(0,2,3)
      ## columns title
      #titre des colonnes
        table_item.add_line([("th",[],class_forms.Text("")),("th",[],class_forms.Text(_("Début"))), ("th",[],class_forms.Text(_("Fin"))), ("th",[],class_forms.Text(_("Description"))) ])
      ## Entry list
      #liste des entree
        i = 0;
        for it in items:
          item_choo = class_forms.Content("","").add_complex_tag("div")
          item_choo.add_input("checkbox","check_"+str(i),"")
          item_choo.add_input("hidden","begin_"+str(i),it["begin"])
          item_choo.add_input("hidden","end_"+str(i),it["end"])
          item_choo.add_input("hidden","text_"+str(i),it["text"])
          
          table_item.add_line([("td",[],item_choo),("td",[],class_forms.Text(self.parse_date(it["begin"]))), ("td",[],class_forms.Text(self.parse_date(it["end"]))), ("td",[],class_forms.Text(it["text"])) ])
          i=i+1
        form_choo.add_input("hidden","nb_it",str(i))
        form_choo.add_input("submit","submit",_("Importer"))
        self.db.drop(self.table_prefix+"_temp")
      else:
        pass
    else:
      ## Entry list menu
      #menu de liste des entrees
      body = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      list = body.add_complex_tag("fieldset")
      list.add_simple_tag("legend",_("Liste des événements"))

      items = (self.db.table(self.table_prefix+"_items")).select( order=[("begin",True)])
      p = list.add_complex_tag("p") 
      table_item = p.add_table(0,2,3)
      ## columns title
      #titre des colonnes
      table_item.add_line([("th",[],class_forms.Text(_("Début"))), ("th",[],class_forms.Text(_("Fin"))), ("th",[],class_forms.Text(_("Description"))), ("th",[],class_forms.Text("")) ])
      ## Entry list
      #liste des entree
      for it in items:
        form_ed = class_forms.Content("","").add_form("admin.py","get")
        ed = form_ed.add_complex_tag("p")
        ed.add_input("hidden", "id", "Calendars")
        ed.add_input("hidden","action", "edit")
        ed.add_input("hidden","item_id", str(it["id"]))
        ed.add_input("submit", "", _("Éditer")) 
        table_item.add_line([("td",[],class_forms.Text(self.parse_date(it["begin"]))), ("td",[],class_forms.Text(self.parse_date(it["end"]))), ("td",[],class_forms.Text(it["text"])), ("td",[],form_ed) ])

      ## Entry adding form
      #formulaire d'ajout d'une entree
      form_add = table_item.add_form( "adminvalid.py?id=Calendars&amp;action=add","post")
      form_add.add_line([("td",[],self.form_date("","begin")), ("td",[],self.form_date("","end")), ("td",[],class_forms.Input_maxlength( "text","item_text","",30)), ("td",[],class_forms.Input( "submit", "submit", _("Ajouter"))) ])
      
      p = list.add_complex_tag("p")
      p.add_br() 
    ## ___ End of page ___
    # ___ Bas de la page ___
    form_page.gen_nav()

