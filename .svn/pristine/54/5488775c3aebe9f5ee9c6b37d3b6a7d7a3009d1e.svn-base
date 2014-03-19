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
## TODO:
##  - everything
# TODO:
#   - tout

from module_interfaces import *

from conf import confstatic
import conf_general, conf_private
from interface import class_forms
from db import db_manager
import re
import datetime



class TheModule(ComfortModule, IModuleContentProvider, IModuleDB, IModuleAdminPage):
  mode        = "both"

  def module_init(self):
    self.table_prefix = "news"
    pass

  def module_admin_info(self):
    return "Permet d'ajouter des news à votre page web."
  
  def module_title(self):
    return _("News")

  def module_name(self):
    return _("News")

  def module_id(self):
    return "News"

  def init_content(self):
    pass

  def handle_admin_request(self, params, fields):
    try:
      form = params["form"]
    except:
      form=""

    ## Adding a course in the database
    # Ajout d'un enseignement dans la BDD
    if form == "add_item":
      if fields.has_key("item_title"):
        record = {  'title'    : fields['item_title'].value, 'date'     : fields['item_date'].value, 'text'     : fields['item_text'].value}
        table_db = self.db.table(self.table_prefix+"_items")
        table_db.insert(record)
        return "admin.py?id=News"
      else:
        return "handler.py"

    ## Deletion of some news
    #effacement d'une news
    elif form == "del_item":
      if fields.has_key("item_id"):
        table = self.db.table(self.table_prefix+"_items")
        table.delete([("id", "=", fields["item_id"].value)])
        return "admin.py?id=News"
      else:
        return "handler.py"

    ## News edition
    # edition d'une news
    elif form == "edit_item":
      if fields.has_key("item_id"):   
        record = {'title'  : fields['item_title'].value, 'date'   : fields['item_date'].value, 'text'   : fields['item_text'].value}

        table_db = self.db.table(self.table_prefix+"_items")
        table_db.update(record, [("id", "=", fields["item_id"].value)])
        return "admin.py?id=News"
      else:
        return "handler.py"

    return "admin.py"

  ## Form to administrate the news
  # Le formulaire d'administration des news 
  def generate_admin_xhtml(self, form_page):
    main = 0
    ## Options list
    # Liste des options                       
    try:
      if form_page.params["form"] == "add_item":
        main = 1
      elif form_page.params["form"] == "edit_item":
        main = 1
    except:
      pass

    title=_("Administration des news")
    form_page.page = class_forms.Page(title,conf_general.style)
    title_content  = form_page.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    form_page.gen_nav()

    ## The whole module menu:
    # Tout le menu du module: 
    body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
    body = body_content.add_complex_tag("fieldset")
    body.add_simple_tag("legend",_("Opérations sur les news"))


    table_f = body.add_table(0,0,5)
    ## News manager button
    # Bouton de gestion des news
    form_main = (class_forms.Content("", "")).add_form( "admin.py?id=News","post")
    form_main.add_input("submit", "submit", _("Gestion générale")) 
    ## Adding news button
    # Bouton d'ajout d'une news
    form_add = (class_forms.Content("", "")).add_form( "admin.py?id=News&amp;form=add_item","post")
    form_add.add_input("submit", "submit", _("Ajouter une news")) 

    table_f.add_line([("td", [], form_main), ("td", [], form_add)])

    p = form_page.page.add_complex_tag("p")
    p.add_br()


    # ___________________________________________________________________ #
    #                                                                     #
    ##                       Main form                                   ##
    #                    Formulaire principal                             #
    # ___________________________________________________________________ #
    if main == 0:
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("News enregistrées"))
      
      ## Retrieve all the news
      # On recupere toutes les news 
      table_db = self.db.table(self.table_prefix + "_items")
      news_db = table_db.select(cond = [], order = [("id",True)])
      if len(news_db) == 0:
        body.add_simple_tag("h3", _("Il n'y a aucune news"))
      else: 
        body.add_simple_tag("h3", _("Il y a ")+str(len(news_db))+ _(" news dans la base de données"))

        table_f = body.add_table(1,0,1)
        table_f.add_line([("th",[("align","center")],
                               class_forms.Text(_("Titre de la news"))), ("th",[("align","center")], class_forms.Text(_("Date"))), ("th",[("align","center")], class_forms.Text(_("Actions"))) ])

        for news in news_db:
          ## The nice buttons on the right
          # Les p'tits boutons mignons de la droite
          commands = (class_forms.Content("", "")).add_table(0, 0, 2)
          form_del = (class_forms.Content("", "")).add_form( "adminvalid.py?id=News&amp;form=del_item","post")
          form_del.add_input("hidden", "item_id", str(news["id"]))
          form_del.add_input("submit", "submit", _("Supprimer")) 

          form_edit = (class_forms.Content("", "")).add_form( "admin.py?id=News&amp;form=edit_item&amp;item_id=" +str(news["id"]),"post")
          form_edit.add_input("submit", "submit", _("Éditer")) 

          commands.add_line([("td", [], form_del), ("td", [], form_edit)])

          table_f.add_line([ ("td",[("align","left")], class_forms.Text(news['title'])), ("td",[("align","left")], class_forms.Text(news['date'])), ("td",[("align","left")], commands) ])

      body2 = body.add_complex_tag("p");
      body2.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                         Adding news form                          ##
    #                    Formulaire d'ajout d'une news                    #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == "add_item":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Ajouter une news"))
    
      ## Adding form
      # Le formulaire d'ajout
      form = body.add_form("adminvalid.py?id=News&amp;form=add_item", "post")
      p = form.add_complex_tag("p")

      text_f = class_forms.Content("","")
      text_f.add_textarea("item_text",10,50)

      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_title", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Date")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_date",  (datetime.date.today()).strftime("%d-%m-%Y") ))\
                 ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Description")+" : ")), ("td",[("align","left")], text_f) ])
      p.add_br()
      p.add_input("submit", "submit", _("Ajouter la news"))
      p.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                       News edition form                           ##
    #                  Formulaire d'édition d'une news                    #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == "edit_item":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Édition d'une news"))

      table_db = self.db.table(self.table_prefix+"_items")
      news_db = table_db.select(cond=[("id", "=", form_page.params["item_id"])], order=[("id",True)]).next()

      form = body.add_form("adminvalid.py?id=News&amp;form=edit_item", "post")
      p = form.add_complex_tag("p")
      p.add_input("hidden","item_id",form_page.params["item_id"])

      text_f = class_forms.Content("","")
      text_f = text_f.add_textarea("item_text",10,50)
      text_f.add_text(news_db['text'])

      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_title", news_db["title"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Date")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_date", news_db["date"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Texte")+" : ")), ("td",[("align","left")], text_f) ])
      p.add_br()
      p.add_input("submit", "submit", _("Éditer la news"))

    ## __ End of the page __
    # ___ Bas de la page ___
    form_page.gen_nav()



  # __________________________________________________________________________#

  def generate_content_xml(self, args):
    ch = ""
    
    
    ## All the news are retrieved
    # On recupere toutes les news 
    table_db    = self.db.table(self.table_prefix+"_items")
    news_db = table_db.select(cond=[],order=[("id",True)])
    for n in news_db:
      ch += "  <sect2>\n"
      ch += "    <title>"+n['title']+" ::: le "+n['date']+"</title>\n"
      ch += n['text']
      ch += "  </sect2>\n"
    
    
    return ch

  def setup_db(self, db):
    self.db    = db
    ## News table ceation: modify the types of course...
    # Création de la table des news : modifier les types bien sûr...
    schema = {'title': 'text', 'date' : 'text', 'text' :'text'}
    try:
      self.db.table(self.table_prefix+"_items")
    except:
      self.db.create(self.table_prefix+"_items", schema);

   
    
    
