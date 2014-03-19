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
## - Managing documents (distinguishing Courses/Exercices/Corrections ...)
## - Suppressing files when suppressing a course
## - If the document already exist, do whatever
## Write the documentation
# TODO:
#  - Gestion des documents (distinction TD/Cours/Correction, etc.)
#  - Suppression des fichiers lors d'une suppression d'un enseignement
#  - Si un document existe déjà, faire quelque chose
#
#  - Basculer configuration du module
#  - Dans le nouvel affichage, enlever les pages générées si enseignement supprimé
#  - 
# Faire la doc

from module_interfaces import *


from conf import confstatic
import conf_general, conf_private
from interface import class_forms
from db import db_manager
import re
import os
import module_manager


class TheModule(ComfortModule, IModuleContentProvider, IModuleDB, IModuleAdminPage):
  mode        = "both"

  def module_init(self):
    self.table_prefix = "educ"
    self.title_size   = 25
    self.mm = module_manager.ModuleManager()
    self.modules = self.mm.get_available_modules()

  def module_admin_info(self):
    return "Permet de gérer les enseignements."
  
  def module_title(self):
    return _("Enseignements")

  def module_name(self):
    return _("Enseignements")

  def module_id(self):
    return "Enseignements"

  def init_content(self):
    pass


  def setup_db(self, db):
    self.db    = db

    ## Teachings table creation
    # création de la table des enseignements
    schema = {'title'      : 'varchar',\
              'school'     : 'int',\
              'desc'       : 'text',\
              'type'       : 'text',\
              'year'       : 'varchar',\
              'bib_desc'   : 'text',\
              'bib_list'   : 'varchar',\
              #'short_desc' : 'varchar',\
              'level'      : 'varchar'}
    try:
      self.db.table(self.table_prefix+"_items")
    except:
      self.db.create(self.table_prefix+"_items", schema);

    ## Schools table creation
    # création de la table des établissements
    schema = {'name'   : 'varchar'}
    try:
      self.db.table(self.table_prefix+"_schools")
    except:
      self.db.create(self.table_prefix+"_schools", schema);

    ## Documents table creation
    # création de la table des documents
    schema = {'file'    : 'varchar',\
              'id_educ' : 'int',\
              'desc'    : 'varchar',\
              'title'   : 'varchar',\
              'other'   : 'varchar' }
    try:
      self.db.table(self.table_prefix+"_docs")
    except:
      self.db.create(self.table_prefix+"_docs", schema);

  def handle_admin_request(self, params, fields):
    try:
      form = params["form"]
    except:
      form=""

    ## Adding a course in the database
    # Ajout d'un enseignement dans la BDD
    if form == "add_item":
      if fields.has_key("item_title"):
        ## If a school has to be added
        # si on doit rajouter un établissement 
        if (fields['item_school'].value == "-1"):
          record_school = { 'name' : fields['new_school'].value }
          table_db = self.db.table(self.table_prefix+"_schools")
          item_school = table_db.insert(record_school) - 1
        else:
          item_school = fields['item_school'].value     
       
        record = {'title'      : fields['item_title'].value, \
                  'school'     : item_school, \
                  'year'       : fields['item_year'].value, \
                  'type'       : fields['item_type'].value, \
                  'desc'       : fields['item_desc'].value,\
                  'bib_desc'   : '',\
                  'bib_list'   : '-1', \
                #  'short_desc' : '',\
                  'level'      : fields['item_level'].value}

        table_db = self.db.table(self.table_prefix+"_items")
        table_db.insert(record)
        return "admin.py?id=Educ"
      else:
        return "handler.py"
    
    ## Edition of a course
    # Edition d'un enseignement
    elif form == "edit_item":
      if fields.has_key("item_id"):
        ## If a school needs to be added
        # si on doit rajouter un établissement 
        if (fields['item_school'].value == "-1"):
          record_school = { 'name' : fields['new_school'].value }
          table_db = self.db.table(self.table_prefix+"_schools")
          item_school = table_db.insert(record_school) - 1
        else:
          item_school = fields['item_school'].value     
 
        record = {'title'   : fields['item_title'].value, 'school'   : item_school, 'year'     : fields['item_year'].value, 'type'     : fields['item_type'].value, 'bib_list' : fields['item_bib'].value, 'desc'     : fields['item_desc'].value, 'level'    : fields['item_level'].value}

        table_db = self.db.table(self.table_prefix+"_items")
        table_db.update(record, [("id","=",fields["item_id"].value)])
        return "admin.py?id=Educ"
      else:
        return "handler.py"
    
    ## Deletion of a course in the database
    # Suppression d'un enseignement dans la BDD 
    elif form == "del_item":
      if fields.has_key("item_id"):
        table_db = self.db.table(self.table_prefix+"_items")
        table_db.delete([("id", "=", fields["item_id"].value)])

        table_db = self.db.table(self.table_prefix+"_docs")
        table_db.delete([("id_educ", "=", fields['item_id'].value)])
        
        return "admin.py?id=Educ"
      else:
        return "handler.py"

    ## Edition of a document
    # Edition d'un document
    elif form == "edit_doc":
      if fields.has_key("doc_id"):

        if fields.has_key("doc_path"):
          fileitem = fields["doc_path"]
          if fileitem.file:
            try:      
              if fields.has_key("item_id"):
                name_f = fields["item_id"].value + "_" + (fileitem.filename)    
                fout = file (os.path.join(confstatic.docs_path, name_f), 'wb')
            except:
              return "admin.py?id=Educ"
      
            fout.write(fileitem.file.read())
            fout.close()
            
          if fileitem.filename != "":
            record = {'title'    : fields['doc_title'].value,\
                      'desc'     : fields['doc_desc'].value,\
                      'file' : name_f\
                      }
          else:
            record = {'title' : fields['doc_title'].value,\
                      'desc'  : fields['doc_desc'].value\
                     }
                
        table_db = self.db.table(self.table_prefix+"_docs")
        table_db.update(record, [("id","=",fields["doc_id"].value)])
        return "admin.py?id=Educ&amp;form=add_doc&amp;item_id="+fields['item_id'].value
      else:
        return "handler.py"

    ## Deletion of a document in the database
    # Suppression d'un document dans la BDD 
    elif form == "del_doc":
      if fields.has_key("doc_id"):
        table = self.db.table(self.table_prefix+"_docs")
        table.delete([("id", "=", fields["doc_id"].value)])
         
        os.remove(os.path.join(confstatic.docs_path, fields['doc_name'].value))
        return "admin.py?id=Educ&amp;form=add_doc&amp;item_id="+fields['item_id'].value
      else:
        return "handler.py"

    ## Erasing the whole table
    # Effacement de toute la table
    elif form == "erase_all":
      table = self.db.table(self.table_prefix+"_items")
      table.delete([])
      table = self.db.table(self.table_prefix+"_docs")
      table.delete([])
      return "admin.py?id=Educ"

    ## Bibliography adding
    # Ajout d'une bibliographie
    elif form == "add_bibli":
      if fields.has_key("item_id"):
        record = {'bib_desc'   : fields["bib_desc"].value, 'bib_list'   :  fields["bib_list"].value}

        table_db = self.db.table(self.table_prefix+"_items")
        table_db.update(record, [("id","=",fields["item_id"].value)])
        return "admin.py?id=Educ"
      else:
        return "handler.py"


    ## Document adding to a course
    # Ajout d'un document à un enseignement
    elif form == "add_doc":
      if fields.has_key("doc_path"):
        fileitem = fields["doc_path"]
        if fileitem.file:
          try:      
            if fields.has_key("item_id"):
              name_f = fields["item_id"].value + "_" + (fileitem.filename)
              fout = file (os.path.join(confstatic.docs_path, name_f), 'wb')
          except:
            return "admin.py?id=Educ"

          while 1:
              buff = fileitem.file.read(100000)
              if not buff: break
              fout.write (buff)
          fout.close()

          record = {  'title'    : fields['doc_title'].value, 'desc'     : fields['doc_desc'].value, 'id_educ'  : fields['item_id'].value, 'file'     : name_f, 'other'    : ""}

          table_db = self.db.table(self.table_prefix+"_docs")
          table_db.insert(record)
          return "admin.py?id=Educ&amp;form=add_doc&amp;item_id="+fields["item_id"].value
        else:
          return ""
      else:
        return "handler.py"
    else:
      return "handler.py"
  
  ## The form to administrate the courses
  # Le formulaire d'administration des enseignements 
  def generate_admin_xhtml(self, form_page):
    
    main = 0                           
    try:
      if form_page.params["form"] == "edit_item":
        main = 2
      elif form_page.params["form"] == "add_item":
        main = 1
      elif form_page.params["form"] == "add_doc":
        main = 1
      elif form_page.params["form"] == "edit_doc":
        main = 1
      elif form_page.params["form"] == "erase_all":
        main = 1
      elif form_page.params["form"] == "special_out":
        main = 1
      elif form_page.params["form"] == "special_out_gen":
        main = 1
      elif form_page.params["form"] == "add_bibli" and ("Publi" in self.modules):
        main = 1
    except:
      pass


    title=_("Gestion des enseignements")
    form_page.page = class_forms.Page(title,conf_general.style)
    title_content  = form_page.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    form_page.gen_nav()

    body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
    body = body_content.add_complex_tag("fieldset")
    body.add_simple_tag("legend",_("Opérations sur les enseignements"))

    table_f = body.add_table(0,0,5)
    ## Button to manage the teachings
    # Bouton de gestion des enseignements
    form_main = (class_forms.Content("", "")).add_form( "admin.py?id=Educ","post")
    form_main.add_input("submit", "submit", _("Gestion générale")) 
    ## Add button
    # Bouton d'ajout
    form_add = (class_forms.Content("", "")).add_form( "admin.py?id=Educ&amp;form=add_item","post")
    form_add.add_input("submit", "submit", _("Ajouter un enseignement")) 
    ## Table erasement button
    # Bouton d'effacement de la table
    form_erase = (class_forms.Content("", "")).add_form( "admin.py?id=Educ&amp;form=erase_all","post")
    form_erase.add_input("submit", "submit", _("Effacer tous les enseignements")) 
    ## Special output mode button
    # Bouton de gestion de l'affichage spécial
    form_spec = (class_forms.Content("", "")).add_form( "admin.py?id=Educ&amp;form=special_out","post")
    form_spec.add_input("submit", "submit", _("Affichages alternatifs")) 

    table_f.add_line([("td", [], form_main),\
                      ("td", [], form_add),\
                      ("td", [], form_erase),\
                      ("td", [], form_spec)])

    p = form_page.page.add_complex_tag("p")
    p.add_br()


    # ___________________________________________________________________ #
    #                                                                     #
    ##                         Main form                                 ##
    #                     Formulaire principal                            #
    # ___________________________________________________________________ #
    if main == 0: 
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Liste des enseignements"))
        
      ## All the teachings are retrieved
      # On recupere tous les enseignements 
      dbtable = self.db.table(self.table_prefix + "_items")
      enseign = dbtable.select(cond = [], order=[("id", True)])


      if len(enseign) == 0:
        body.add_simple_tag("h3", _("Il n'y a aucun enseignement enregistré"))
      else: 
        table_f = body.add_table(1,0,1)

        if 'Publi' in self.modules:
          table_f.add_line([("th",[("align","center")],
                                 class_forms.Text(_("Intitulé du cours"))), ("th",[("align","center")], class_forms.Text(_("Établissement"))), ("th",[("align","center")], class_forms.Text(_("Type"))), ("th",[("align","center")],\
                                 class_forms.Text(_("Année"))), ("th",[("align","center")], class_forms.Text(_("Niveau (L3/M1/etc.)"))), ("th",[("align","center")], class_forms.Text(_("Documents"))), ("th",[("align","center")], class_forms.Text(_("Bibliographie"))), ("th",[("align","center")],\
                                 class_forms.Text(_("Actions"))) ])
        else:
          table_f.add_line([("th",[("align","center")],
                                 class_forms.Text(_("Intitulé du cours"))), ("th",[("align","center")], class_forms.Text(_("Établissement"))), ("th",[("align","center")], class_forms.Text(_("Type"))), ("th",[("align","center")],\
                                 class_forms.Text(_("Année"))), ("th",[("align","center")], class_forms.Text(_("Niveau (L3/M1/etc.)"))), ("th",[("align","center")], class_forms.Text(_("Documents"))), ("th",[("align","center")], class_forms.Text(_("Actions"))) ])

        for cours_db in enseign:
          ## The nice button on the right
          # Les p'tits boutons mignons de la droite
          commands = (class_forms.Content("", "")).add_table(0, 0, 2)
          form_del = (class_forms.Content("", "")).add_form( "adminvalid.py?id=Educ&amp;form=del_item","post")
          form_del.add_input("hidden", "item_id", str(cours_db["id"]))
          form_del.add_input("submit", "submit", _("Supprimer")) 

          form_edit = (class_forms.Content("", "")).add_form( "admin.py?id=Educ&amp;form=edit_item&amp;item_id="+ str(cours_db["id"])+"","post")
          form_edit.add_input("submit", "submit", _("Éditer")) 

          commands.add_line([("td", [], form_del), ("td", [], form_edit)])

          documents = class_forms.Content("", "").add_form( "admin.py?id=Educ&amp;form=add_doc&amp;item_id="+(str(cours_db["id"])),"post")
          documents.add_input("submit", "submit", _("Gestion des documents"))
 
          bibli = class_forms.Content("", "").add_form( "admin.py?id=Educ&amp;form=add_bibli&amp;item_id="+(str(cours_db["id"])),"post")
          bibli.add_input("submit", "submit", _("Bibliographie")) 

          ## Fields are cut if too long
          # On coupe les champs si ils sont trop longs
          if len(cours_db['title']) < self.title_size:
            title = class_forms.Text(cours_db['title'])
          else:
            title = class_forms.Text(cours_db['title'][0:self.title_size] + '...')
        
          school = class_forms.Text(self.give_school(cours_db['school']))
 
          if cours_db['type'] == "0":
            type = "TD"
          else:
            type = "cours"

          if 'Publi' in self.modules:
            table_f.add_line([ ("td",[("align","left")], title), \
                               ("td",[("align","left")], school), \
                               ("td",[("align","left")], class_forms.Text(type)), \
                               ("td",[("align","left")], class_forms.Text(cours_db['year'])), \
                               ("td",[("align","left")], class_forms.Text(cours_db['level'])), \
                               ("td",[("align","left")], documents),\
                               ("td",[("align","left")], bibli), \
                               ("td",[("align","right")], commands) ])
          else:
            table_f.add_line([ ("td",[("align","left")], title), ("td",[("align","left")], school), ("td",[("align","left")], class_forms.Text(type)), ("td",[("align","left")], class_forms.Text(cours_db['year'])), ("td",[("align","left")], class_forms.Text(cours_db['level'])),\
                 ("td",[("align","left")], documents), ("td",[("align","right")], commands) ])

      body2 = body.add_complex_tag("p");
      body2.add_br()
  

    # ___________________________________________________________________ #
    #                                                                     #
    ##                         Adding a course form                      ##
    #                     Formulaire d'ajout d'enseignement               #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == "add_item":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Ajout d'un enseignement"))
      
      p = body.add_complex_tag("p")
      p.add_text( "<script language=\"javascript\" type=\"text/javascript\">\n /* <![CDATA[ */\n function change_form(action){\n if (action == -1)\n document.getElementById('formulaire').new_school.type = 'text';\n\
          else\n document.getElementById('formulaire').new_school.type = 'hidden';\n }\n /* ]]> */\n </script>")


      ## The so-called form !
      # Le formulaire à proprement parler !
      form = p.add_complex_option_tag("form",[ ("action" , "adminvalid.py?id=Educ&amp;form=add_item"),
          ("method" , "post"),
          ("id"     , "formulaire")])
      p = form.add_complex_tag("p")
      
      table_f = p.add_table(0, 0, 3)
      table_f.add_line([("td", [("align","left")], class_forms.Text(_("Intitulé du cours")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_title", "")) ])
      

      schools_l = self.give_schools()
      num_schools = len(schools_l)

      if (num_schools == 0):
        select_opt = [([("value", "-1"),("selected","selected")], _("Nouvel établissement"))]
      else:
        select_opt = [([("value", "-1")], _("Nouvel établissement"))]
        
      for school_i in schools_l:
        select_opt.append(([("value", str(school_i[0])),("selected","selected")], school_i[1]))
      
      select_f = (class_forms.Content("","")).add_complex_option_tag("select", [("name","item_school"),("onchange","javascript:change_form(item_school.value)")])


      for opt in select_opt:
        temp = select_f.add_complex_option_tag("option", opt[0])
        temp.add_text(opt[1])


      select_type = (class_forms.Content("","")).add_complex_option_tag("select", [("name","item_type")])

      temp = select_type.add_complex_option_tag("option", [("value", "0")])
      temp.add_text("TD")
      temp = select_type.add_complex_option_tag("option", [("value", "1")])
      temp.add_text("cours")

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Etablissement")+" : ")), ("td",[("align","left")], select_f) ])
      if num_schools == 0:
        table_f.add_line([("td",[("align","left")], class_forms.Text("")), ("td",[("align","left")], class_forms.Input("text", "new_school", "Ecole des Acacias")) ])
      else:
        table_f.add_line([("td",[("align","left")], class_forms.Text("")), ("td",[("align","left")], class_forms.Input("hidden", "new_school", "Ecole des Acacias")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Année (ex: \"2007-2008\")")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_year", "2007-2008")) ])

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Niveau")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_level", "")) ])

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Type de l'enseignement")+" : ")), ("td",[("align","left")], select_type) ])

      truc = class_forms.Content("","")
      truc.add_textarea("item_desc",10,50)

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Description")+" : ")), ("td",[("align","left")], truc) ])
      p.add_br()
      p.add_input("submit", "submit", _("Ajouter l'enseignement"))


    # ___________________________________________________________________ #
    #                                                                     #
    ##                        Edition form                               ##
    #                     Formulaire d'édition         : XHTML 1.0 strict #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == 'edit_item':
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Édition d'un enseignement"))
     

      ## Let's retrieve all the information available for the course to edit
      # Recuperons toutes les infos disponibles pour l'enseignement a editer
      table_db = self.db.table(self.table_prefix + "_items")
      enseign_db = table_db.select(cond = [("id","=",form_page.params["item_id"])], order = [("id",True)]).next()

      p = body.add_complex_tag("p")

      p.add_text( "<script language=\"javascript\" type=\"text/javascript\">\n /* <![CDATA[ */\n function change_form(action){\n if (action == -1)\n document.getElementById('formulaire').new_school.type = 'text';\n\
          else\n document.getElementById('formulaire').new_school.type = 'hidden';\n }\n /* ]]> */\n </script>")


      ## The so-called form !
      # Le formulaire à proprement parler !
      form = p.add_complex_option_tag("form",[ ("action" , "adminvalid.py?id=Educ&amp;form=edit_item"),
          ("method" , "post"),
          ("id"     , "formulaire")])
      p = form.add_complex_tag("p")
      p.add_input("hidden","item_id",form_page.params["item_id"])
      
      table_f = p.add_table(0, 0, 3)
      table_f.add_line([("td", [("align","left")], class_forms.Text(_("Intitulé du cours")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_title", enseign_db['title'].replace('&', '&amp;'))) ])
      

      schools_l = self.give_schools()
      num_schools = len(schools_l)

      if (num_schools == 0):
        select_opt = [([("value", "-1"),("selected","selected")], _("Nouvel établissement"))]
      else:
        select_opt = [([("value", "-1")], _("Nouvel établissement"))]
        
      for school_i in schools_l:
        if str(school_i[0]) == str(enseign_db['school']):
          select_opt.append(([("value", str(school_i[0])),("selected","selected")], school_i[1]))
        else:
          select_opt.append(([("value", str(school_i[0]))], school_i[1]))        
      
      select_f = (class_forms.Content("","")).add_complex_option_tag("select", [("name","item_school"),("onchange","javascript:change_form(item_school.value)")])

      for opt in select_opt:
        temp = select_f.add_complex_option_tag("option", opt[0])
        temp.add_text(opt[1])


      select_type = (class_forms.Content("","")).add_complex_option_tag("select", [("name","item_type")])

      if (enseign_db['type'] == "0"):
        temp = select_type.add_complex_option_tag("option", 
          [("value", "0"),("selected","selected")])
        temp.add_text("TD")
        temp = select_type.add_complex_option_tag("option", [("value", "1")])
        temp.add_text("cours")
      else:
        temp = select_type.add_complex_option_tag("option", [("value", "0")])
        temp.add_text("TD")
        temp = select_type.add_complex_option_tag("option", 
          [("value", "1"),("selected","selected")])
        temp.add_text("cours")


      ## If Publishings module is activated
      # Si on a le module de Publications
      if 'Publi' in self.modules:
        table_db = self.db.table(self.mm['Publi'].table_prefix+"_lists")
        list_db = table_db.select(cond=[] , order = [("id",True)])
        select_opt = []
  
        for list_i in list_db:
          if str(list_i['id']) == enseign_db['bib_list']:
            select_opt.append(([("value", str(list_i['id'])),("selected","selected")], list_i['title']))
          else:
            select_opt.append(([("value", str(list_i['id']))], list_i['title']))

        select_bib = (class_forms.Content("","")).add_complex_option_tag("select", [("name","item_bib")])
        temp = select_bib.add_complex_option_tag("option", [("value", "-1"),("selected","selected")])
        temp.add_text("Aucune bibliographie")
  
        for opt in select_opt:
          temp = select_bib.add_complex_option_tag("option", opt[0])
          temp.add_text(opt[1])


      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Établissement")+" : ")), ("td",[("align","left")], select_f) ])
      if num_schools == 0:
        table_f.add_line([("td",[("align","left")], class_forms.Text("")), ("td",[("align","left")], class_forms.Input("text", "new_school", "Ecole primaire Jean Moulin")) ])
      else:
        table_f.add_line([("td",[("align","left")], class_forms.Text("")), ("td",[("align","left")], class_forms.Input("hidden", "new_school", "Ecole primaire Jean Moulin")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Année (ex: \"2007-2008\")")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_year", enseign_db['year'])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Niveau")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_level", enseign_db['level'])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Type d'enseignement")+" : ")), ("td",[("align","left")], select_type) ])

      if 'Publi' in self.modules:
        table_f.add_line([("td",[("align","left")], class_forms.Text(_("Bibliographie")+" : ")), ("td",[("align","left")], select_bib) ])

      truc = class_forms.Content("","")
      g = truc.add_textarea("item_desc",10,50)
      g.add_text(enseign_db['desc'])

      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Description")+" : ")), ("td",[("align","left")], truc) ])
      p.add_br()
      p.add_input("submit", "submit", _("Éditer l'enseignement"))

    # ___________________________________________________________________ #
    #                                                                     #
    ##                       Erasing all the table                       ##
    #                     Effacement de toute la table                    #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == "erase_all":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Effacement de tous les enseignements"))

      form = body.add_form("adminvalid.py?id=Educ&amp;form=erase_all", "post")
      form.add_br()
      form.add_input("submit", "submit", "Oui, je veux TOUT effacer")

    # ___________________________________________________________________ #
    #                                                                     #
    ##                      Adding documents form                        ##
    #                     Formulaire d'ajout de documents                 #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == 'add_doc':
      dbtable = self.db.table(self.table_prefix+"_items")
      enseign = dbtable.select(cond=[("id", "=", form_page.params["item_id"])],order=[("id",True)])

      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      for l in enseign:
        body.add_simple_tag("legend", "Gestion des documents :: " +l["title"])

      ## Adding form
      # Le formulaire d'ajout
      form = body.add_complex_option_tag("form", [("action", "adminvalid.py?id=Educ&amp;form=add_doc"), ("method", "post"), ("enctype","multipart/form-data")])
      p = form.add_complex_tag("p")
      p.add_input("hidden", "item_id", form_page.params["item_id"]) 


      ## The description
      # La description
      desc = class_forms.Content("","")
      desc.add_textarea("doc_desc", 6, 50)
      ## File to upload
      # Le fichier à uploader
      file_i = class_forms.Content("","")
      file_i.add_single_tag("input", [("type", "file"), ("name", "doc_path"), ("accept", "*/*")])

      ## Table generation (actually form generation)
      # Génération de la table (le formulaire en fait)    
      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre du fichier")+" : ")), ("td",[("align","left")], class_forms.Input("text", "doc_title", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Description")+" : ")), ("td",[("align","left")], desc) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Fichier à uploader")+" : ")), ("td",[("align","left")], file_i) ])
      ## End of the table
      # fin de la table


      p.add_br()
      p.add_input("submit", "submit", _("Ajouter le document"))
  
      body_content.add_br()

      ## LIST OF THE DOCUMENTS
      # LISTE DES DOCUMENTS
      #
      table_db = self.db.table(self.table_prefix+"_docs")
      docs_db = table_db.select(cond = [("id_educ", "=", form_page.params["item_id"])], order = [("id",True)])
      body2 = body_content.add_complex_tag("fieldset")
      body2.add_simple_tag("legend", 'Liste des documents attachés')
  
      table_f = body2.add_table(1,0,1)
      table_f.add_line([("th",[("align","center")],
                               class_forms.Text(_("Nom du document"))), ("th",[("align","center")], class_forms.Text(_("Nom du fichier"))), ("th",[("align","center")], class_forms.Text(_("Description"))),\
                      ("th",[("align","center")], class_forms.Text(_("Actions"))) ])

      for doc in docs_db:
        ## Nice buttons on the right
        # Les p'tits boutons mignons de la droite
        commands = (class_forms.Content("", "")).add_table(0, 0, 2)
        form_del = (class_forms.Content("", "")).add_form( "adminvalid.py?id=Educ&amp;form=del_doc","post")
        form_del.add_input("hidden", "doc_id", str(doc["id"]))
        form_del.add_input("hidden", "doc_name", str(doc["file"]))
        form_del.add_input("hidden", "item_id", str(doc["id"]))
        form_del.add_input("submit", "submit", _("Supprimer")) 

        form_edit = (class_forms.Content("", "")).\
          add_form("admin.py?id=Educ&amp;form=edit_doc&amp;item_id="+form_page.params['item_id']+"&amp;doc_id="+str(doc['id']),"post")
        form_edit.add_input("submit", "submit", _("Editer")) 

        commands.add_line([("td", [], form_edit),("td", [], form_del)])

        ## Fields are cut if too long
        # On coupe les champs si ils sont trop longs
        if len(doc['desc']) < self.title_size:
          desc = class_forms.Text(doc['desc'])
        else:
          desc = class_forms.Text(doc['desc'][0:self.title_size] + '...')

        table_f.add_line([ ("td",[("align","left")], class_forms.Text(doc['title'])),\
                           ("td",[("align","left")], class_forms.Text(doc['file'])), \
                           ("td",[("align","left")], desc), \
                           ("td",[("align","right")], commands) ])

  
      body2 = body.add_complex_tag("p");
      body2.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                        Document editing form                      ##
    #                     Formulaire d'édition de document                #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == 'edit_doc':
      dbtable = self.db.table(self.table_prefix+"_items")
      e = dbtable.select(cond=[("id", "=", form_page.params["item_id"])],order=[("id",True)]).next()
      dbtable = self.db.table(self.table_prefix+"_docs")
      l = dbtable.select(cond=[("id", "=", form_page.params["doc_id"])],order=[("id",True)]).next()

      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend", "Edition du document :: " + e["title"] + " :: " + l['title'])

      ## Adding form
      # Le formulaire d'ajout
      form = body.add_complex_option_tag("form", [("action", "adminvalid.py?id=Educ&amp;form=edit_doc"), \
                                                  ("method", "post"), \
                                                  ("enctype","multipart/form-data")])
      p = form.add_complex_tag("p")
      p.add_input("hidden", "item_id", form_page.params["item_id"]) 
      p.add_input("hidden", "doc_id", form_page.params["doc_id"]) 


      ## The description
      # La description
      desc = class_forms.Content("","")
      desc.add_textarea("doc_desc", 6, 50).add_text(l['desc'])

      ## File to upload
      # Le fichier à uploader
      file_i = class_forms.Content("","")
      file_i.add_single_tag("input", [("type", "file"), ("name", "doc_path"), ("accept", "*/*")])

      ## Table generation (form actually)
      # Génération de la table (le formulaire en fait)    
      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre du fichier")+" : ")), ("td",[("align","left")], class_forms.Input("text", "doc_title", l['title'])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Description")+" : ")), ("td",[("align","left")], desc) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Fichier à uploader")+" : ")), ("td",[("align","left")], file_i) ])
      ## End of the table
      # fin de la table


      p.add_br()
      p.add_input("submit", "submit", _("Appliquer les modifications"))
  
      body_content.add_br()


    # ___________________________________________________________________ #
    #                                                                     #
    ##                         Adding bibliography form                  ##
    #                     Formulaire d'ajout de bibliographie             #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == 'add_bibli':
      dbtable = self.db.table(self.table_prefix+"_items")
      enseign = dbtable.select(cond=[("id", "=", form_page.params["item_id"])],order=[("id",True)])

      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      for l in enseign:
        body.add_simple_tag("legend", "Gestion des documents :: " +l["title"])

      ## Adding form
      # Le formulaire d'ajout
      form = body.add_complex_option_tag("form", [("action", "adminvalid.py?id=Educ&amp;form=add_bibli"), ("method", "post"), ("enctype","multipart/form-data")])
      p = form.add_complex_tag("p")
      p.add_input("hidden", "item_id", form_page.params["item_id"]) 


      ## Description
      # La description
      desc = class_forms.Content("","")
      desc.add_textarea("bib_desc", 6, 50)

      ## The publishings
      # Les publications
      table_db = self.db.table(self.mm['Publi'].table_prefix+"_lists")
      list_db = table_db.select(cond=[] , order = [("id",True)])
      select_opt = []
      for list_i in list_db:
        select_opt.append(([("value", str(list_i['id'])),("selected","selected")], list_i['title']))
      select_f = (class_forms.Content("","")).add_complex_option_tag("select", [("name","bib_list")])
      for opt in select_opt:
        temp = select_f.add_complex_option_tag("option", opt[0])
        temp.add_text(opt[1])

      ## Table generation (form generation actually)
      # Génération de la table (le formulaire en fait)    
      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Description")+" : ")), ("td",[("align","left")], desc) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Bibliographie")+" : ")), ("td",[("align","left")], select_f) ])
      ## End of the table
      # fin de la table

      p.add_br()
      p.add_input("submit", "submit", _("Ajouter le document"))
  
      body_content.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                         Special outputs form                      ##
    #                       Formulaire Affichages spéciaux                #
    # ___________________________________________________________________ #
    elif form_page.params['form'] == 'special_out':

      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend", _("Message d'avertissement"))
    
      body.add_text("<br/>"+_("ATTENTION: VOUS DEVEZ AVOIR LE MODULE WIKI POUR UTILISER CETTE FONCTIONNALITE<br/><br/> vous pouvez sur cette page choisir parmis les différents affichages alternatifs proposés à l'affichage sur une unique page. Cela signifie que le module Educ va créer pour vous un certain nombre de pages wiki nécessaires. Celles-ci n'apparaitront pas de base dans le menu. Elles seront accessibles via le menu Gestion des Pages de l'administration pour toute personnalisation. De plus, le code à insérer pour afficher les enseignements vous sera indiqué ici. Vous devrez l'insérer dans la page wiki de votre choix."))

      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend", _("Gestion des affichages alternatifs"))

      p = body.add_complex_tag("p")
      form = p.add_complex_option_tag("form", [ ("action" , "admin.py?id=Educ&amp;form=special_out_gen"),
                                                ("method" , "post"),
                                                ("id"     , "short_form")])

      p = form.add_complex_tag("p")
      
      p.add_br()
      p.add_input("submit", "submit", _("Génerer les pages"))

    elif form_page.params['form'] == 'special_out_gen':

      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend", _("Pages générées"))
    
      table_db = self.db.table(self.table_prefix + "_items")
      enseign_db = table_db.select(cond = [], order = [("id", True)])


      body.add_br()
      body.add_text(_('Voici le code wiki à insérer dans votre la page souhaitée'))
      body.add_br()
      toinsert = body.add_textarea("", 3, 50).add_text('<module id="Educ" params="type=short" />')
      body.add_br()

      for e in enseign_db:
        p_id = "Educ_"+e['title'][0:3]+str(e['id'])
        body.add_text('<br/>'+ p_id + '.html '+_('générée'))

        table_page = self.db.table(confstatic.pages_database_prefix)
        enreg_page = {"page_id" : p_id, "page_title": e['title'], }
        for m in self.modules:
          if isinstance(self.mm[m], IModuleContentProvider):
            if m == confstatic.module_wiki_name:
              enreg_page[m + "_priority"] = 0
            elif m == "Menu":
              enreg_page[m + "_priority"] = 1
            else:
              enreg_page[m + "_priority"] = -1
        
        enreg_page["page_wiki"]='<module id="Educ" params="req=single&id='+str(e['id'])+'" />'
        table_page.insert(enreg_page)

        
    
    ## __ End of the page __
    # ___ Bas de la page ___
    form_page.gen_nav()


  def generate_content_xml(self, args):
    ch = ""
      
    if args.has_key('req'):
      req = args['req']
    else:
      req = "main"


    if req == "single":
      if args.has_key('id'):
        try:
          table_db    = self.db.table(self.table_prefix+"_items")
          enseign_db = table_db.select(cond = [("id", "=", args['id'])], order=[("id",True)])
          e = enseign_db.next()
          ch += "  <sect2>\n"
          ch += "    <title>"+e['title']+" ::: "+self.give_school(e['school'])+", "+e['level']+", "+e['year']+"</title>\n"
         
          ch += "    <itemizedlist>\n"
          ch += "      <listitem>"+e['desc']+"<para></para></listitem>\n"
             

          table_db    = self.db.table(self.table_prefix+"_docs")
          docs_db = table_db.select(cond=[("id_educ", "=", e['id'])],order=[("id", True)])

          if len(docs_db) > 0:
            ch += "      <listitem><emphasis role='strong'>"+_("Documents :")+"</emphasis>\n"
            ch += "        <itemizedlist>\n"
            for doc in docs_db:
              ch += "        <listitem><ulink url='"+confstatic.get_docs_url(doc['file'])+"'>"+doc['title']+ "</ulink> - "+doc['desc']+"</listitem>\n"
        
            ch += "        </itemizedlist>\n"
            ch += "      <para></para>\n"
            ch += "      </listitem>\n"

          if e['bib_list'] != "-1":
            ch += "     <listitem><emphasis role='strong'>"+_("Bibliographie")+":</emphasis>\n"
            ch += "       <itemizedlist>"
            ch += "         <para>"+e['bib_desc']+"</para>\n"

            publi_list = []

            if 'Publi' in self.modules:
              publi_list = self.give_publications_from_list(0)
                      
            for p in publi_list:
              ch += "         <listitem>"

              if p['pdf'] == "":   
                ch += ("""<ulink url="#"><emphasis role=\"strong\">%s</emphasis></ulink>""")\
                       %(self.pub_display(p['title']))
              else:
                ch += ("""<ulink url="%s"><emphasis role=\"strong\">%s</emphasis></ulink>""")\
                        %(confstatic.get_docs_url(p['pdf']), self.pub_display(p['title']))
              
              ch += _("de")+" "+p['author']+"</listitem>"

            ch += "       </itemizedlist>"
            ch += "     </listitem>\n"
          ch += "    </itemizedlist>\n"
          ch += "  </sect2>\n"
        except:
          pass
      else:
        pass

    # ___________________________________________________________________ #
    #                                                                     #
    ##                         Main Education page                       ##
    #                      Page principale des enseignements              #
    # ___________________________________________________________________ #
    else:
      ## Different modes of displaying
      # Différents modes d'affichage de la page principale
      if args.has_key('type') and args['type'] == 'short':      
        table_db    = self.db.table(self.table_prefix+"_items")
        enseign_db = table_db.select(cond=[],order=[("id",True)])
        for e in enseign_db:
          ch += "  <sect2>\n"
          ch += "    <itemizedlist>\n"
          
          ch += "      <listitem>"
          if e['type'] != "":
            if e['type'] == '0':
              ch += "TDs de "
            elif e['type'] == '1':
              ch += "Cours de "
            elif e['type'] == '2':
              ch += "TPs de "
      
  
          p_id = "Educ_"+e['title'][0:3]+str(e['id'])
          ch += "<emphasis role='strong'>" + "<ulink url='" \
                      + confstatic.build_url({"page":p_id+".html"})  + "'>" + e['title'] + "</ulink></emphasis>  "
          if e['level'] != "":
            ch += "("+e['level']
            if e['year'] != "":
              ch += ", "+e['year']
            ch += ")."
          elif e['year'] != "":
            ch += "("+e['year']+")."
          ch += "      </listitem>"

          ch += "    </itemizedlist>\n"
          ch += "  </sect2>\n"

      ## Default display mode
      # Mode d'affichage par défaut
      else: 
        ## Retrieving all the courses
        # On recupere tous les enseignements 
        table_db    = self.db.table(self.table_prefix+"_items")
        enseign_db = table_db.select(cond=[],order=[("id",True)])
        for e in enseign_db:
          ch += "  <sect2>\n"
          ch += "    <title>"+e['title']+" ::: "+self.give_school(e['school'])+", "+e['level']+", "+e['year']+"</title>\n"
         
          ch += "    <itemizedlist>\n"
          ch += "      <listitem>"+e['desc']+"<para></para></listitem>\n"
             

          table_db    = self.db.table(self.table_prefix+"_docs")
          docs_db = table_db.select(cond=[("id_educ", "=", e['id'])],order=[("id", True)])

          if len(docs_db) > 0:
            ch += "      <listitem><emphasis role='strong'>"+_("Documents")+":</emphasis>\n"
            ch += "        <itemizedlist>\n"
            for doc in docs_db:
              ch += "        <listitem><ulink url='"+confstatic.get_docs_url(doc['file'])+"'>"+doc['title']+"</ulink> - "+doc['desc']+"</listitem>\n"
        
            ch += "        </itemizedlist>\n"
            ch += "      <para></para>\n"
            ch += "      </listitem>\n"

          if e['bib_list'] != "-1":
            ch += "     <listitem><emphasis role='strong'>"+_("Bibliographie")+":</emphasis>\n"
            ch += "       <itemizedlist>"
            ch += "         <para>"+e['bib_desc']+"</para>\n"

            publi_list = []

            if 'Publi' in self.modules:
              publi_list = self.give_publications_from_list(0)
                      
            for p in publi_list:
              ch += "         <listitem>"

              if p['pdf'] == "":   
                ch += ("""<ulink url="#"><emphasis role=\"strong\">%s</emphasis></ulink>""")\
                       %(self.pub_display(p['title']))
              else:
                ch += ("""<ulink url="%s"><emphasis role=\"strong\">%s</emphasis></ulink>""")\
                        %(confstatic.get_docs_url(p['pdf']), self.pub_display(p['title']))
              
              ch += _("de")+" "+p['author']+"</listitem>"

            ch += "       </itemizedlist>"
            ch += "     </listitem>\n"
          ch += "    </itemizedlist>\n"
          ch += "  </sect2>\n"
    return ch


  ## It is given the ID of a publis list, it sends back a publis list
  # 
  # On lui donne l'ID d'une liste de publi, et il renvoie une liste de publis ! 
  def give_publications_from_list (self, id_list):
    try:
      res = []
      table_db   = self.db.table("publi" + "_lists")
      lists_db = table_db.select(cond = [("id","=",id_list)], order = [("id", True)])
      list_db = lists_db.next()

      next = list_db['pub_list']
      tmp  = re.match('-([^-]*)(-.*)', next)
      next = tmp.group(2)
      table_db   = self.db.table("publi" + "_items")
      for item_i in (table_db.select(cond = [("id","=",tmp.group(1))], order = [("id", True)])):
        res.append(item_i)
      while tmp.group(2) != '-':
        tmp  = re.match('-([^-]*)(-.*)', next)
        next = tmp.group(2)
        for item_i in (table_db.select(cond = [("id","=",tmp.group(1))], order = [("id", True)])):
          res.append(item_i)
      
      return res
    except:
      return None
   
    return res

  def give_schools(self):
    res = []
    table_db   = self.db.table(self.table_prefix + "_schools")
    schools_db = table_db.select(cond = [], order = [("id", True)])
    for school_db in schools_db:
      res.append((str(school_db['id']), school_db['name']))
    return res
    
  def give_school(self, id_school):
    res = ''
    table_db = self.db.table(self.table_prefix + "_schools")
    school_name = table_db.select(cond =[("id", "=", id_school)], order = [("id", True)])
    for l in school_name:
      res = l['name']
    return res
    
  def handle_request(self, request):
    pass

  def pub_display(self, title):
    ch = ""
    ch = title
    ch = ch.replace('{', '')
    ch = ch.replace('}', '')
    ch = ch.replace("\\`a", "à")
    ch = ch.replace("\\'e", "é")
    ch = ch.replace("\\`e", "è")
    ch = ch.replace("\\^e", "ê")
    return ch
