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
from module_interfaces import *


from conf import confstatic
from conf import utils
import conf_general, conf_private
from db import db_manager
from interface import class_forms

import urllib
class TheModule(ComfortModule, IModuleContentProvider, IModuleDB,  IModuleAdminPage):

  mode = "both"

  def module_init(self):
    self.database_prefix="menu"


  def module_admin_info(self):
    return "Permet d'afficher un menu sur vos pages."


  def module_title(self):
    return ""


  def module_name(self):
    return confstatic.module_menu_name

  def module_id(self):
    return "Menu"


  def init_content(self):
    pass


  def generate_content_xml(self, args):
    """ 
      Génère les boutons du menu
    """
    menu=self.db.table(self.database_prefix+"_items"). select(cond=[],order=[("id",True)])
    str = "<itemizedlist>\n"
    in_submenu = False
    count = 0
    for e in menu:
      if e["is_comfort"]!=0:
        url = confstatic.build_url({"page":urllib.quote(e["item_link"])+".html"})
      else:
        url = confstatic.get_pages_url(e["item_link"])
      if e["item_depth"] == 1 and not in_submenu:
        str += "\n\t<itemizedlist>"
        in_submenu = True
      elif e["item_depth"] == 0 and not in_submenu and count > 0:
        str += "</listitem>\n"
        in_submenu = False
      elif e["item_depth"] == 1 and in_submenu:
        str += "</listitem>\n"
        in_submenu = True
      elif e["item_depth"] == 0 and in_submenu:
        str += "</listitem></itemizedlist></listitem>\n"
        in_submenu = False
      str += ("""<listitem><ulink url=\"%s\">%s</ulink>\n""" )%(url,
          utils.sanitize(e["item_text"]))
      count += 1

    if not in_submenu:
      str += "</listitem>\n"
      in_submenu = False
    elif in_submenu:
      str += "</listitem></itemizedlist></listitem>\n"
      in_submenu = False

    str += "</itemizedlist>"
    return str


  def setup_db(self, db):
    """
      Test si la base de données existe.
      Champs de la base de données:
        - item_text: varchar --> le texte du bouton
        - item_link: varchar --> la page vers laquelle pointe le bouton
        - is_comfort: integer --> 0 : le bouton pointe vers une page perso: ./perso/pages/item_link
                                  non 0 : le bouton pointe vers la page item_link de comfort
    """
    self.db = db
    try:
      self.db.table(self.database_prefix+"_items")
    except:
      self.db.create(self.database_prefix+"_items", {"item_depth": "integer", "item_text": "varchar","item_link": "varchar", "is_comfort": "integer"})
      menu=self.db.table(self.database_prefix+"_items")
      menu.insert({"item_text" :confstatic.default_page_name,"item_link" :confstatic.default_page_name, "is_comfort": 1, "item_depth": 0})
      menu.insert({"item_text" :confstatic.wikisyntax_page_name,"item_link" :confstatic.wikisyntax_page_name, "is_comfort": 1, "item_depth": 0})



  def explore_dir_pages_perso(self,selected,options,prefix):
    """    
      Crée les options du <select> HTML avec les pages persos
    """
    try:
      pages=os.listdir(os.path.join(confstatic.pages_path,prefix))
      dirs=[]
      for p in pages:
        if os.path.isdir(os.path.join(confstatic.pages_path,prefix,p)):
          dirs.append(p)
        else:
          (path,ext)=os.path.splitext(p)
          if ext[1:] in confstatic.pages_perso_extensions:
            item=os.path.join(prefix,p)
            if item==selected:
              options.append(([("value","0"+item),("selected","selected")],item))
            else:
              options.append(([("value","0"+item)],item))        
      for d in dirs:    
        self.explore_dir_pages_perso(selected,options,os.path.join(prefix,d))
    except:
      pass
  
  
  def handle_admin_request(self, params, fields):
    try:
      form=params["form"]
    except:
      form=""
    table=self.db.table(self.database_prefix+"_items")
    if form=="item_del":
      if fields.has_key("item_id"):
        ## It is rubbish, but it will go for now
        #C'est tout pourri, mais pour l'instant ça suffit
        size=len(table.select(cond = []))
        but_id=fields["item_id"].value
        table.delete([("id","=",but_id)])
        ## Bottom buttons id are decremented
        ## It is a harsh but the menu is surely not
        ## composed of 1000 buttons and it will make
        ## the operations to sort the buttons easier
        #on décrémente les id des boutons du dessous
        #c'est un peu lourd mais le menu ne comporte
        #surement pas 10000 boutons et ca facilite les
        #opération pour ordonner les boutons
        for i in range(int(but_id)+1,size):
          table.update({"id":i-1},[("id","=",i)])
        
        return "admin.py?id=Menu"
      else:
        return "handler.py"

    elif form=="item_up":
      if fields.has_key("item_id"):
        target_but=str(int(fields["item_id"].value)-1)
        table.update({"id":-1},[("id","=", fields["item_id"].value)])
        table.update({"id":int(fields["item_id"].value)}, [("id","=",target_but)])
        table.update({"id":target_but},[("id","=",-1)])
        return "admin.py?id=Menu"
      else:
        return "handler.py"

    elif form=="item_down":  
      if fields.has_key("item_id"):
        target_but=str(int(fields["item_id"].value)+1)
        table.update({"id":-1},[("id","=", fields["item_id"].value)])
        table.update({"id":int(fields["item_id"].value)}, [("id","=",target_but)])
        table.update({"id":target_but},[("id","=",-1)])
        return "admin.py?id=Menu"
      else:
        return "handler.py"

    elif form=="iteml":
      if fields.has_key("item_id"):
        table.update({"item_depth":0},[("id","=",fields["item_id"].value)])
        return "admin.py?id=Menu"
      else:
        return "handler.py"
  
    elif form=="itemr":
      if fields.has_key("item_id"):
        table.update({"item_depth":1},[("id","=",fields["item_id"].value)])
        return "admin.py?id=Menu"
      else:
        return "handler.py"
  
    elif form == "item_edit":
      if fields.has_key("item_id") and fields.has_key("item_text") and fields.has_key("item_link"):
        is_comfort=int(fields["item_link"].value[0:1])
        link=fields["item_link"].value[1:]
        if fields["item_id"].value!="-1":
          table.update({"id":fields["item_id"].value, "item_text":fields["item_text"].value, "item_link":link, "is_comfort":is_comfort},
                       [("id","=",fields["item_id"].value)])
        else:
          ## The button did not exist, now it does
          #le bouton n'existait pas: on l'ajoute
          table.insert({"id":fields["item_id"].value,
            "item_text":fields["item_text"].value, "item_link":link,
            "is_comfort":is_comfort, "item_depth":0})
        return "admin.py?id=Menu"
      else:
        return "handler.py"

    else:
      return "handler.py"


  def generate_admin_xhtml(self, form_page):
    """
      Formulaire de gestion du menu:


      Formulaire de gestion de l'ordre des éléments du menu
      Validation a effectuer: (via adminvalid.py?id=Menu&form=x)
      *** A stocker dans la BDD, table: "menu_items" ***
      - form=item_up: Faire monter le boutton item_id dans le menu
        *** Champs envoyes par POST ***
        - item_id
      - form=item_down: Faire descendre le boutton item_id dans le menu
        *** Champs envoyes par POST ***
        - item_id
      - form=item_del: Supprimer le boutton item_id
        *** Champs envoyes par POST ***
        - item_id


      Formulaire de gestion des éléments du menu
      Validation a effectuer: (via adminvalid.py?id=Menu&form=x)
      - form=item_edit: Mettre a jour les infos concernant le bouton item_id
        *** Champs envoyés par POST ***
        *** A stocker dans la BDD, table: "menu_items" ***
        - item_id
        - item_text
        - item_link : correspond au champ page_id de la page à charger
    """
    main=True    ##General form or peculiar form ??
                 #Formulaire général ou propre à un item ??
    try:
      if form_page.params["form"]=="item":
        if form_page.params.has_key("item_id"): ## id of item to modify
                                                #id de l'item a modifier
          main=False
    except:
      pass
    
    title=_("Gestion du menu")
    form_page.page = class_forms.Page(title,conf_general.style)
    title_content=form_page.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    form_page.gen_nav()

    body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
    body = body_content.add_complex_tag("fieldset")
    body.add_simple_tag("legend",_("Opérations sur le menu"))


    table_f = body.add_table(0,0,5)
    ## Button for the main form
    # Bouton de gestion générale
    form_main = (class_forms.Content("", "")).add_form( "admin.py?id=Menu","post")
    form_main.add_input("submit", "submit", _("Gestion générale")) 
    ## New button 
    # Nouveau bouton
    form_add = (class_forms.Content("", "")).add_form( "admin.py?id=Menu&amp;form=item&item_id=-1","post")
    form_add.add_input("submit", "submit", _("Ajouter un bouton au menu")) 

    table_f.add_line([("td", [], form_main), ("td", [], form_add)])

    p = form_page.page.add_complex_tag("p")
      
    if main:
      ################## Main form #################
      ############ Formulaire principal ############
      body_content=form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body=body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Liste des boutons du menu"))


      ## Retrieving all the information in the database
      # on recupère toutes les infos dans la bdd
      menu=self.db.table(self.database_prefix+"_items"). select(cond=[],order=[("id",True)])

      if len(menu)==0:
        body.add_simple_tag("p",_("Le menu est vide."))
      else:
        body.add_simple_tag("p",_("Voici la liste des boutons du menu:"))
        table = body.add_table(1,0,3)

        table.add_line([("th",[("align","center")],class_forms.Text( "Texte du bouton")), ("th",[("align","center")],class_forms.Text( "Lien")), ("th",[("align","center")],class_forms.Text( "Actions")) ])
        maxi=len(menu)-1
        count=0
        for e in menu:
          buttons=(class_forms.Content("","")).add_table(0,0,3)

          form1=(class_forms.Content("","")).add_form( "adminvalid.py?id=Menu&form=item_up","post")
          form1.add_input("hidden","item_id",str(e["id"]))
          opt=[("type","submit"),("name","submit"),("value",_("Monter"))]
          if count==0:
            opt.append(("disabled","disabled"))
          form1.add_single_tag("input",opt)

          form2=(class_forms.Content("","")).add_form( "adminvalid.py?id=Menu&form=item_down","post")
          form2.add_input("hidden","item_id",str(e["id"]))
          opt=[("type","submit"),("name","submit"),("value",_("Descendre"))]
          if count==maxi:
            opt.append(("disabled","disabled"))
          form2.add_single_tag("input",opt)

          form3=(class_forms.Content("","")).add_form( """admin.py?id=Menu&form=item&item_id=%d"""%(e["id"]),"post")
          form3.add_input("submit","submit", _("Editer"))

          form4=(class_forms.Content("","")).add_form( "adminvalid.py?id=Menu&form=item_del","post")
          form4.add_input("hidden","item_id",str(e["id"]))
          form4.add_input("submit","submit", _("Supprimer")) 

          form5=(class_forms.Content("","")).add_form("adminvalid.py?id=Menu&form=iteml","post")
          form5.add_input("hidden","item_id",str(e["id"]))
          opt=[("type","submit"),("name","submit"),("value","&lt;")]
          if e["item_depth"] == 0:
            opt.append(("disabled","disabled"))
          form5.add_single_tag("input",opt)

          form6=(class_forms.Content("","")).add_form("adminvalid.py?id=Menu&form=itemr","post")
          form6.add_input("hidden","item_id",str(e["id"]))
          opt=[("type","submit"),("name","submit"),("value","&gt;")]
          if e["item_depth"] == 1 or count == 0:
            opt.append(("disabled","disabled"))
          form6.add_single_tag("input",opt)

          buttons.add_line([("td",[],form1),("td",[],form2),("td",[],form3), ("td",[],form4), ("td",[],form5), ("td",[],form6)])

          name = class_forms.Content("","")
          if e["item_depth"] == 1:
            name.add_complex_option_tag("img", [("src", "../styles/admin/format-indent-more.png")])
          name.add_text(e["item_text"])
          table.add_line([ ("td",[("align","left")],name), ("td",[("align","left")],class_forms.Text(e["item_link"])), ("td",[("align","right")],buttons) ])
          count+=1

      p = body.add_complex_tag("p")
    
      form_page.gen_nav()
    else:
      ################ Form for an item ###############
      ## Get the information in the database
      ############ Formulaire pour un item ############
      # Recuperer les infos dans la base de donnees
      item_id=int(form_page.params["item_id"])
      if item_id!=-1:
        item=self.db.table(self.database_prefix+"_items"). select(cond=[("id","=",item_id)],order=[("id",True)]).next()
      else:
        item={"id"  : item_id, "item_text":_("Nouveau bouton"), "item_link" :confstatic.default_page_name, "item_depth":0}

      ## Options for the scrolling menu are made
      #on fabrique les options pour le menu déroulant
      possible_pages=self.db.table("pages").select(cond=[])
      options=[]
      for o in possible_pages:
        if item["item_link"]==o["page_id"]:
          options.append(([("value","1"+o["page_id"]),("selected","selected")], o["page_id"]))
        else:
          options.append(([("value","1"+o["page_id"])],o["page_id"]))
          
      pages_perso=[]
      self.explore_dir_pages_perso(item["item_link"],pages_perso,"")

      if len(pages_perso)!=0:
        options.append(([("disabled","disabled")],"--- "+_("Pages personnelles") + " ---"))
        options=options+pages_perso
        
      select=class_forms.Select("item_link",options)
      ## End of database information
      # Fin infos bdd

      ## Page generation
      #on genere la page   
      body_content=form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body=body_content.add_complex_tag("fieldset")
      if form_page.params["item_id"]!="-1":
        body.add_simple_tag("legend",_("Modification du bouton")+" \""+ item["item_text"]+"\"")      
      else:
        body.add_simple_tag("legend",_("Ajout d'un bouton"))
      form = body.add_form("adminvalid.py?id=Menu&form=item_edit", "post")      
      form.add_input("hidden","item_id",form_page.params["item_id"])
      p = form.add_complex_tag("p")
      table=p.add_table(0,0,3)
      table.add_line([("td",[("align","left")],class_forms.Text( _("Nom du bouton")+" : ")), ("td",[("align","left")],class_forms.Input_maxlength( "text","item_text", item["item_text"],100)) ])
      table.add_line([("td",[("align","left")],class_forms.Text( _("Lien")+" : ")), ("td",[("align","left")],select) ])
      
      p = form.add_complex_tag("p")
      p.add_input("submit", "submit", _("Appliquer"))
 
      form_page.gen_nav()
