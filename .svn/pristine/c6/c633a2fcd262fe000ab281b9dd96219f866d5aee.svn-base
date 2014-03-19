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
## 
#
# TODO:
#  MISE EN FORME
#  Ajout de photo

from module_interfaces import *


from conf import confstatic
import conf_general, conf_private
from interface import class_forms
from db import db_manager
import re



class TheModule(ComfortModule, IModuleContentProvider, IModuleDB, IModuleAdminPage):
  mode        = "both"

  def module_init(self):
    self.table_prefix = "coord"
    pass

  def module_admin_info(self):
    return "Permet d'ajouter vos coordonnées."
  
  def module_title(self):
    return ""

  def module_name(self):
    return _("Coordonnées")

  def module_id(self):
    return "Coord"

  def init_content(self):
    pass

  def handle_admin_request(self, params, fields):
    try:
      form = params["form"]
    except:
      form=""

    ## Adding a coord set in the database
    # Ajout d'un jeu de coordonnées dans la BDD
    if form == "add_item":
      if fields.has_key("item_title"):
        record = {'f_name'      : fields['item_f_name'].value,     \
                  'l_name'      : fields['item_l_name'].value,     \
                  'tel1'        : fields['item_tel1'].value,       \
                  'tel2'        : fields['item_tel2'].value,       \
                  'tel1_text'   : fields['item_tel1_text'].value,  \
                  'tel2_text'   : fields['item_tel2_text'].value,  \
                  'addr_perso'  : fields['item_addr_perso'].value, \
                  'addr_work'   : fields['item_addr_work'].value,  \
                  'mail'        : fields['item_mail'].value,       \
                  'fax'         : fields['item_fax'].value,        \
                  'labo'        : fields['item_labo'].value,       \
                  'title'       : fields['item_title'].value,      \
                  'labo_url'    : fields['item_labo_url'].value}

        table_db = self.db.table(self.table_prefix+"_items")
        table_db.insert(record)
        return "admin.py?id=Coord"
      else:
        return "handler.py"

    ## Deletion of some coords
    # effacement d'un jeu de coordonnées
    elif form == "del_item":
      if fields.has_key("item_id"):
        table = self.db.table(self.table_prefix+"_items")
        table.delete([("id", "=", fields["item_id"].value)])
        return "admin.py?id=Coord"
      else:
        return "handler.py"

    ## Coords edition
    # edition d'un jeu de coordonnée
    elif form == "edit_item":
      if fields.has_key("item_id"):   

        record = {'f_name'      : fields['item_f_name'].value,     \
                  'l_name'      : fields['item_l_name'].value,     \
                  'tel1'        : fields['item_tel1'].value,       \
                  'tel2'        : fields['item_tel2'].value,       \
                  'tel1_text'   : fields['item_tel1_text'].value,  \
                  'tel2_text'   : fields['item_tel2_text'].value,  \
                  'addr_perso'  : fields['item_addr_perso'].value, \
                  'addr_work'   : fields['item_addr_work'].value,  \
                  'mail'        : fields['item_mail'].value,       \
                  'fax'         : fields['item_fax'].value,        \
                  'labo'        : fields['item_labo'].value,       \
                  'title'       : fields['item_title'].value,      \
                  'labo_url'    : fields['item_labo_url'].value}

        table_db = self.db.table(self.table_prefix+"_items")
        table_db.update(record, [("id", "=", fields["item_id"].value)])
        return "admin.py?id=Coord"
      else:
        return "handler.py"

    return "admin.py"

  ## Form to administrate the coords
  # Le formulaire d'administration des coordonnées 
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

    title=_("Module coordonnées")
    form_page.page = class_forms.Page(title,conf_general.style)
    title_content  = form_page.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    form_page.gen_nav()

    ## The whole module menu:
    # Tout le menu du module: 
    body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
    body = body_content.add_complex_tag("fieldset")
    body.add_simple_tag("legend",_("Opérations sur les jeux de coordonnées"))


    table_f = body.add_table(0,0,5)
    ## News manager button
    # Bouton de gestion des news
    form_main = (class_forms.Content("", "")).add_form( "admin.py?id=Coord","post")
    form_main.add_input("submit", "submit", _("Gestion générale")) 
    ## Adding news button
    # Bouton d'ajout d'une news
    form_add = (class_forms.Content("", "")).add_form( "admin.py?id=Coord&amp;form=add_item","post")
    form_add.add_input("submit", "submit", _("Ajouter un jeu de coordonnées")) 

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
      body.add_simple_tag("legend",_("Coordonnées enregistrées"))
      
      ## Retrieve all the coord
      # On recupere tous les jeux de coordonnées 
      table_db = self.db.table(self.table_prefix + "_items")
      coord_db = table_db.select(cond = [], order = [("id",True)])
      if len(coord_db) == 0:
        body.add_simple_tag("h3", _("Il n'y a aucun jeu de coordonnées"))
      else: 
        if len(coord_db) == 1:
          body.add_simple_tag("h3", _("Il y a ")+"1"+ _(" jeu de coordonnées"))
        else:
          body.add_simple_tag("h3", _("Il y a ")+str(len(coord_db))+ _(" jeux de coordonnées"))


        table_f = body.add_table(2,0,4)
        table_f.add_line([("th",[("align","center")], class_forms.Text(_("Titre"))), \
                          ("th",[("align","center")], class_forms.Text(_("Tel1"))), \
                          ("th",[("align","center")], class_forms.Text(_("Tel2"))),\
                          ("th",[("align","center")], class_forms.Text(_("mail"))),\
                          ("th",[("align","center")], class_forms.Text(_("fax"))),\
                          ("th",[("align","center")], class_forms.Text(_("labo")))\
                        ])

        for coord in coord_db:
          ## The nice buttons on the right
          # Les p'tits boutons mignons de la droite
          commands = (class_forms.Content("", "")).add_table(0, 0, 2)
          form_del = (class_forms.Content("", "")).add_form( "adminvalid.py?id=Coord&amp;form=del_item","post")
          form_del.add_input("hidden", "item_id", str(coord["id"]))
          form_del.add_input("submit", "submit", _("Supprimer")) 

          form_edit = (class_forms.Content("", "")).add_form( "admin.py?id=Coord&amp;form=edit_item&amp;item_id=" +str(coord["id"]),"post")
          form_edit.add_input("submit", "submit", _("Éditer")) 

          commands.add_line([("td", [], form_del), ("td", [], form_edit)])

          table_f.add_line([("td",[("align","left")], class_forms.Text(coord['title'])), \
                            ("td",[("align","left")], class_forms.Text(coord['tel1'])),\
                            ("td",[("align","left")], class_forms.Text(coord['tel2'])),\
                            ("td",[("align","left")], class_forms.Text(coord['mail'])),\
                            ("td",[("align","left")], class_forms.Text(coord['fax'])),\
                            ("td",[("align","left")], class_forms.Text(coord['labo'])),\
                            ("td",[("align","left")], commands) ])

      body2 = body.add_complex_tag("p");
      body2.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                         Adding coord form                          ##
    #                    Formulaire d'ajout d'un jeu de coordonnées       #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == "add_item":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Ajouter un jeu de coordonnées"))
    
      ## Adding form
      # Le formulaire d'ajout
      form = body.add_form("adminvalid.py?id=Coord&amp;form=add_item", "post")
      p = form.add_complex_tag("p")

      addr_work_t = class_forms.Content("","")
      addr_work_t = addr_work_t.add_textarea("item_addr_work",10,50) 

      addr_perso_t = class_forms.Content("","")
      addr_perso_t = addr_perso_t.add_textarea("item_addr_perso",10,50) 


      p.add_input("hidden","item_tel1_text", "")
      p.add_input("hidden","item_tel2_text", "")


      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre du jeu de coordonnées")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_title", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Nom")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_f_name", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Prenom")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_l_name", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Telephone 1")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_tel1", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Telephone 2")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_tel2","")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Fax")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_fax", "")) ])

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Adresse perso")+" : ")), \
                        ("td",[("align","left")], addr_perso_t) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Adresse travail")+" : ")), \
                        ("td",[("align","left")], addr_work_t) ])

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Mail")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_mail", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Laboratoire")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_labo", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("URL du laboratoire")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_labo_url", "")) ])


      p.add_br()
      p.add_input("submit", "submit", _("Ajouter le jeu de coordonnées"))
      p.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                       Coord edition form                           ##
    #                  Formulaire d'édition d'un jeu de coordonnées       #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == "edit_item":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Édition d'un jeu de coordonnées"))

      table_db = self.db.table(self.table_prefix+"_items")
      coord_db = table_db.select(cond=[("id", "=", form_page.params["item_id"])], order=[("id",True)]).next()

      form = body.add_form("adminvalid.py?id=Coord&amp;form=edit_item", "post")
      p = form.add_complex_tag("p")
      p.add_input("hidden","item_id",form_page.params["item_id"])
 
      p.add_input("hidden","item_tel1_text", coord_db['tel1_text'])
      p.add_input("hidden","item_tel2_text", coord_db['tel2_text'])


      addr_work_t = class_forms.Content("","")
      addr_work_t = addr_work_t.add_textarea("item_addr_work",10,50)
      addr_work_t.add_text(coord_db['addr_work'])

      addr_perso_t = class_forms.Content("","")
      addr_perso_t = addr_perso_t.add_textarea("item_addr_perso",10,50)
      addr_perso_t.add_text(coord_db['addr_perso'])

      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre du jeu de coordonnées")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_title", coord_db["title"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Nom")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_f_name", coord_db["f_name"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Prenom")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_l_name", coord_db["l_name"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Telephone 1")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_tel1", coord_db["tel1"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Telephone 2")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_tel2", coord_db["tel2"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Fax")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_fax", coord_db["fax"])) ])

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Adresse perso")+" : ")), \
                        ("td",[("align","left")], addr_perso_t) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Adresse travail")+" : ")), \
                        ("td",[("align","left")], addr_work_t) ])

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Mail")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_mail", coord_db["mail"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Laboratoire")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_labo", coord_db["labo"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("URL du laboratoire")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_labo_url", coord_db["labo_url"])) ])

      p.add_br()
      p.add_input("submit", "submit", _("Éditer le jeu de coordonnées"))

    ## __ End of the page __
    # ___ Bas de la page ___
    form_page.gen_nav()


  # __________________________________________________________________________#

  def generate_content_xml(self, args):
    ch = ""


    ## All the fields are retrieved
    # On recupere tous les champs 
    table_db    = self.db.table(self.table_prefix+"_items")
    
    ## If a specific coord set is on request
    # Si un jeu spécifique de coordonnées est demandé
    if args.has_key('coord_id'):
      coord_db = table_db.select(cond=[("id", "=", args['coord_id']) ],order=[("id",True)])
    else:
      coord_db = table_db.select(cond=[], order=[("id", True)])
  
    try:
      coord = coord_db.next()  
  
      ch += "  <para>\n"
      ch += "    <emphasis role='strong'>"+coord['title']+"</emphasis><sbr/>\n"
      ch += "    "+coord['f_name']+" "+coord['l_name']+"<sbr/>\n"
 

      ## Tel
      # Téléphone
      if coord['tel1'] != "" and coord['tel1_text'] != "":
        ch += "      <emphasis role='strong'>"+coord['tel1_text']+"</emphasis> "+coord['tel1']+"<sbr/>\n"
      elif coord['tel1'] != "":
        ch += "      <emphasis role='strong'>Tel:</emphasis> "+coord['tel1']+"<sbr/>\n"
      if coord['tel2'] != "" and coord['tel2_text'] != "":
        ch += "      <emphasis role='strong'>"+coord['tel2_text']+"</emphasis> "+coord['tel2']+"\n"
      elif coord['tel2'] != "":
        ch += "      <emphasis role='strong'>Tel:</emphasis> "+coord['tel2']+"<sbr/>\n"

      ch += "    <para><ulink url='"+coord['labo_url']+"'><emphasis role='strong'>"+coord['labo']+"</emphasis></ulink></para>\n"
      if coord['addr_work'] != "":
        ch += "    <para><emphasis role='strong'>- Travail -</emphasis><sbr/>"+coord['addr_work'].replace('\n', '<sbr/>\n')+"</para>\n"
      if coord['addr_perso'] != "":
        ch += "    <para><emphasis role='strong'>- Personnel -</emphasis><sbr/>"+coord['addr_perso'].replace('\n', '<sbr/>\n')+"</para>\n"

      
      ch += "    <para></para><para><emphasis role='strong'>"+coord['mail']+"</emphasis></para>\n"
      ch += "  </para>\n"
    except:
      ch = ""
    
    return ch

  def setup_db(self, db):
    self.db    = db
    ## Coord table ceation
    # Création de la table des coordonnées
    schema = {'f_name'      : 'text', \
              'l_name'      : 'text', \
              'tel1'        : 'text', \
              'tel2'        : 'text', \
              'tel1_text'   : 'text', \
              'tel2_text'   : 'text', \
              'addr_perso'  : 'text', \
              'addr_work'   : 'text', \
              'mail'        : 'text', \
              'title'       : 'text', \
              'fax'         : 'text', \
              'labo'        : 'text', \
              'labo_url'    : 'text'}
    try:
      self.db.table(self.table_prefix+"_items")
    except:
      self.db.create(self.table_prefix+"_items", schema);

   
    
    
