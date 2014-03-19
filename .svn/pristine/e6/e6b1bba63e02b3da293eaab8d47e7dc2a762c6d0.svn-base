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

import os, sys
import urllib
import shutil
from modules import themodule_Wiki as Wiki

try: ## Windows needs stdio set for binary mode for uploading
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass


from conf import confstatic
import conf_general, conf_private
from modules import module_interfaces
from db import db_manager

class Valideur:
  """
  Verifie les entree des formulaires et les insere la ou il faut le cas echeant
  """
  def __init__(self,mm,db,params,fields):
    self.mm=mm
    self.db=db
    self.params=params
    self.fields=fields


  def write_conf(self):     
    """
    reecrit conf/conf_general.py et conf/conf_private.py
    """  
    if self.fields.has_key("title"):
      conf_general.title=self.fields["title"].value
    if self.fields.has_key("language"):
      conf_general.language=self.fields["language"].value
    if self.fields.has_key("style"):
      conf_general.style=self.fields["style"].value
    if self.fields.has_key("adminstyle"):
      conf_general.adminstyle=self.fields["adminstyle"].value
    if self.fields.has_key("display_logo"):
      conf_general.display_logo=self.fields["display_logo"].value
    if self.fields.has_key("transfer_mode"):
      conf_private.transfer_mode=self.fields["transfer_mode"].value
    if self.fields.has_key("server_ftp"):
      conf_private.server_ftp=self.fields["server_ftp"].value
    if self.fields.has_key("user_ftp"):
      conf_private.user_ftp=self.fields["user_ftp"].value
    if self.fields.has_key("pass_ftp"):
      conf_private.pass_ftp=self.fields["pass_ftp"].value
    if self.fields.has_key("root_ftp"):
      conf_private.root_ftp=self.fields["root_ftp"].value
    installed=conf_general.installed
    if self.fields.has_key("pdfmode"):
      conf_general.pdfmode=self.fields["pdfmode"].value

    fconf = open(os.path.join(confstatic.config_path,"conf_general.py"), 'w')
    fconf.write("# -*- encoding: utf-8 -*-\n\n#ATTENTION : Ce fichier est généré par interface/valid_form.py\n\n")
    fconf.write("title = \""+conf_general.title+"\"\n")
    fconf.write("language = \""+conf_general.language+"\"\n")
    fconf.write("style = \""+conf_general.style+"\"\n")
    fconf.write("\n")
    fconf.write("installed = "+str(conf_general.installed)+"\n")
    fconf.write("pdfmode = \""+conf_general.pdfmode+"\"\n")
    fconf.write("adminstyle = \""+conf_general.adminstyle+"\"\n")
    fconf.write("display_logo = "+str(conf_general.display_logo)+"\n")
    fconf.close()

    fconf = open(os.path.join(confstatic.config_path, "conf_private.py"), 'w')
    fconf.write("# -*- encoding: utf-8 -*-\n\n#ATTENTION : Ce fichier est généré par interface/valid_form.py\n\n")
    fconf.write("transfer_mode = \""+conf_private.transfer_mode+"\"\n")
    fconf.write("\n")
    fconf.write("server_ftp = \""+conf_private.server_ftp+"\"\n")
    fconf.write("user_ftp = \""+conf_private.user_ftp+"\"\n")
    # on n'écrit pas le mot de passe... ## we don't write the password
    fconf.write("root_ftp = \""+conf_private.root_ftp+"\"\n")
    # ... ni le serveur SSH ## neither the ssh server
    fconf.close()



  def check_form_install(self):
    if conf_general.installed:
      return check_form_general(self)
    if self.fields.has_key("title") and self.fields.has_key("language") and \
       self.fields.has_key("transfer_mode") and \
         (self.fields["transfer_mode"].value != "FTP" or \
          self.fields["transfer_mode"].value == "FTP" and self.fields.has_key("server_ftp") and self.fields.has_key("user_ftp") and self.fields.has_key("root_ftp")):
      self.write_conf()
      if self.fields["transfer_mode"].value == "FTP" and (self.fields["server_ftp"].value=="" or self.fields["user_ftp"].value==""):
        return "admin.py?id=install&amp;err=incompleteFTP"
      else:
        conf_general.installed=1
        self.write_conf()
        return "handler.py"
    else:
      return "handler.py"


  def check_form_general(self):
    if self.fields.has_key("title") and self.fields.has_key("language") and \
       self.fields.has_key("style"):
      self.db.table("pages").update({"page_style": self.fields["style"].value}, [("page_style", "=", conf_general.style)])
      self.write_conf()
      return "admin.py"
    else:
      return "handler.py"


  def check_form_pass(self):
    if self.fields.has_key("last_pass") and self.fields.has_key("new_pass") and self.fields.has_key("conf_pass"):
      if self.fields["last_pass"].value!=conf_general.password:
        return "admin.py?id=pass&amp;err=incorrectPass"
      elif self.fields["new_pass"].value=="":
        return "admin.py?id=pass&amp;err=emptyPass"
      elif self.fields["new_pass"].value!=self.fields["conf_pass"].value:
        return "admin.py?id=pass&amp;err=incorrectConf"  
      else:
        self.write_conf(False,True)    
        return "admin.py?id=general"
    else:
      return "handler.py"
 
 
  def check_form_delpage(self):
    if self.fields.has_key("submit"):
      if self.fields["submit"].value==_("Supprimer"):
        try:
          shutil.rmtree(os.path.join(confstatic.latex_path,self.fields["page_id"].value))
        except:
          pass
        self.db.table(confstatic.pages_database_prefix).delete([("page_id", "=", self.fields["page_id"].value)])

        modules = self.mm.get_available_modules()
            
        if confstatic.module_menu_name in modules:
          item_link = self.fields['page_id'].value[0:]
          ## the button exists: we delete it.
          #le bouton existe: on le supprime
          table_db = self.db.table(self.mm[confstatic.module_menu_name].database_prefix+"_items")
          ## buttons to delete
          # boutons à supprimer
          menu_it = table_db.select(cond=[("item_link", "=", self.fields['page_id'].value)],order=[("id",False)])          
          size=len(table_db.select(cond = []))
          for b in menu_it:            
            but_id=b["id"]
            table_db.delete([("id","=",str(but_id))])
            ## Bottom buttons id are decremented
            ## It is a harsh but the menu is surely not
            ## composed of 1000 buttons and it will make
            ## the operations to sort the buttons easier
            #on décrémente les id des boutons du dessous
            #c'est un peu lourd mais le menu ne comporte
            #surement pas 10000 boutons et ca facilite les
            #opération pour ordonner les boutons
            for i in range(but_id+1,size):
              table_db.update({"id":i-1},[("id","=",i)])
        return "admin.py?id=pages"
      else:
        return "admin.py?id=pages"
    else:
      return "admin.py?id=pages"


  def check_form_modpage(self):
    if self.fields.has_key("module") and self.fields.has_key("action") and self.fields.has_key("last_id") and self.fields.has_key("page_id") and self.fields.has_key("page_title"):

      table=self.db.table(confstatic.pages_database_prefix)
      ## Non-empty ID ?
      #ID non vide?
      if self.fields["page_id"].value=="":
        return "admin.py?id=modpage&amp;page_id=&amp;err=emptyID"
      for l in self.fields["page_id"].value:
        o = ord(l)
        a = ord('a')
        z = ord('z')
        A = ord('A')
        Z = ord('Z')
        v0 = ord('0')
        v9 = ord('9')
        if not ((o >= a and o <= z) or (o >= A and o <= Z) or (o >= v0 and o <= v9)):
          return "admin.py?id=modpage&amp;page_id=&amp;err=badID"
      ## Unused ID ?
      #ID non utilisé?
      IDExists=False
      if self.fields["page_id"].value!=self.fields["last_id"].value:
        if len(table.select( cond=[("page_id","=",self.fields["page_id"].value)]))!=0:
          self.fields["page_id"].value=self.fields["last_id"].value
          IDExists=True
      if self.fields.has_key("page_style") and self.fields["page_style"] != conf_general.style:
        enreg={"page_id":self.fields["page_id"].value, "page_style":
            self.fields["page_style"].value, "page_title":self.fields["page_title"].value, }
      else:
        enreg={"page_id":self.fields["page_id"].value, "page_title":self.fields["page_title"].value, }
      modules=filter(lambda m: isinstance(self.mm[m],module_interfaces.IModuleContentProvider),self.mm.get_available_modules())
      max_priority=-1
    
      for m in modules:
        enreg[m+"_priority"]=int(self.fields[m+"_priority"].value)
        if enreg[m+"_priority"]>max_priority:
          max_priority=enreg[m+"_priority"]
      
      if self.fields["action"].value=="active_wiki":
        if enreg[confstatic.module_wiki_name+"_priority"]==-1:
          enreg[confstatic.module_wiki_name+"_priority"]=max_priority+1
        return_url="""admin.py?id=modpage&amp;page_id=%s"""% (self.fields["page_id"].value)

      elif self.fields["action"].value=="edit_wiki":
        if enreg[confstatic.module_wiki_name+"_priority"]==-1:
          enreg[confstatic.module_wiki_name+"_priority"]=max_priority+1
        return_url=("""admin.py?id=editpage&amp;page_id=%s""")% (self.fields["page_id"].value)

      elif self.fields["action"].value=="up":
        if enreg[self.fields["module"].value+"_priority"]>-1:
          min_prio=max_priority+1
          min_mod=""
          for m in modules:
            if  enreg[self.fields["module"].value+"_priority"]<enreg[m+"_priority"] and enreg[m+"_priority"]<min_prio:
              min_prio=enreg[m+"_priority"]
              min_mod=m
          if min_mod!="":  ## Security measure, it should be always true
                           #mesure de sécurité, normalement toujours vrai
            enreg[min_mod+"_priority"]= enreg[self.fields["module"].value+"_priority"]
            enreg[self.fields["module"].value+"_priority"]= enreg[self.fields["module"].value+"_priority"]+1
        return_url="""admin.py?id=modpage&amp;page_id=%s"""% (self.fields["page_id"].value)        

      elif self.fields["action"].value=="down":
        if enreg[self.fields["module"].value+"_priority"]>-1:
          max_prio=-1
          max_mod=""
          for m in modules:
            if  enreg[m+"_priority"]<enreg[self.fields["module"].value+"_priority"] and max_prio<enreg[m+"_priority"]:
              max_prio=enreg[m+"_priority"]
              max_mod=m
          if max_mod!="":   ## Security measure, it should be always true
                            #mesure de sécurité, normalement toujours vrai
            enreg[max_mod+"_priority"]= enreg[self.fields["module"].value+"_priority"]
            enreg[self.fields["module"].value+"_priority"]= enreg[self.fields["module"].value+"_priority"]-1
        return_url="""admin.py?id=modpage&amp;page_id=%s"""% (self.fields["page_id"].value)

      elif self.fields["action"].value=="refresh":
        if self.fields[self.fields["module"].value+"_state"].value=="0":
          priority=enreg[self.fields["module"].value+"_priority"]
          for m in modules:
            if enreg[m+"_priority"]>priority:
              enreg[m+"_priority"]-=1
          enreg[self.fields["module"].value+"_priority"]=-1 
        else:
          for m in modules:
            if enreg[m+"_priority"]!=-1 or m==self.fields["module"].value:
              enreg[m+"_priority"]+=1
        return_url="""admin.py?id=modpage&amp;page_id=%s"""% (self.fields["page_id"].value)

      else:
        return_url="admin.py?id=pages"
        
      ## New page ?
      #Nouvelle page?
      if self.fields["last_id"].value!="": ##Already existing page #page déjà existante
        table.update(enreg,[("page_id","=",self.fields["last_id"].value)])
      else:
        ## If page does not exist it is added
        #la page n'existait pas: on l'ajoute
        enreg["page_wiki"]=""
        table.insert(enreg)
        
      table_db = self.db.table(self.mm[confstatic.module_menu_name].database_prefix+"_items")                
      
      if self.fields.has_key('page_addmenu'):
        item_link = self.fields['page_id'].value
        if item_link!="":
          ## If button does not exist it is added
          #le bouton n'existait pas: on l'ajoute            
          table_db.insert({"id":-1, "item_text": self.fields['page_title'].value, "item_link": item_link, "is_comfort": "1","item_depth":0})
      # If the name of the page hase changed, links are updated
      #Si la page a changé de nom, on met à jour les liens
      if self.fields['last_id'].value!="":
        table_db.update({"item_link":self.fields['page_id'].value},[("item_link","=",self.fields["last_id"].value)])        
        
      if IDExists:  
        return """admin.py?id=modpage&amp;page_id=%s&amp;err=existsID"""% (self.fields["page_id"].value)
      else:
        return return_url
    else:
      return "handler.py" 


  def check_form_editpage(self):
    if self.fields.has_key("page_id") and self.fields.has_key("page_wiki") and self.fields.has_key("submit"):
      if self.fields["page_wiki"].value==None:
        self.fields["page_wiki"].value=""
      try:
        if self.fields["submit"].value==_("Appliquer"):
          pages=self.db.table(confstatic.pages_database_prefix)
          pages.update({"page_wiki":self.fields["page_wiki"].value}, [("page_id","=",self.fields["page_id"].value)])        
          return """admin.py?id=modpage&amp;page_id=%s"""%(self.fields["page_id"].value)
        else:
          fp = open(confstatic.overview_path,"w+")
          fp.write(self.fields["page_wiki"].value)
          fp.close()
          return """admin.py?id=editpage&amp;page_id=%s&amp;apercu=1"""%(self.fields["page_id"].value)            
      except:
        return "handler.py"
    else:
      return "handler.py"
      
  ## Checking of form i
  #verification du formulaire numero i
  def check(self):
    ids = { "install"   : self.check_form_install, "general"   : self.check_form_general, "pass"      : self.check_form_pass, "page_del"  : self.check_form_delpage,\
           "page_edit" : self.check_form_modpage, "page_wiki" : self.check_form_editpage}
    
    begin = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" " http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> \n
    <html xmlns="http://www.w3.org/1999/xhtml"> \n <head> \n <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n
          <meta http-equiv="Refresh" content="0;url="""
    end = """" />\n<title></title>\n\
<link rel="stylesheet" href="../styles/admin/%s" type="text/css"  media="screen"/>\n</head>\n<body></body>\n</html>""" % conf_general.adminstyle

    try:
      print begin + ids[self.params["id"]]() + end
    except KeyError:
      try:
        module=self.params["id"]
      except:
        print begin + "handler.py" + end
        return
      modules=self.mm.get_available_modules()
      if module in modules:
        if isinstance(self.mm[module], module_interfaces.IModuleAdminPage):
          print begin + self.mm[module].handle_admin_request( self.params,self.fields) + end
      else:  
        print begin + "handler.py" + end
