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
import urllib

from conf import confstatic
import conf_general, conf_private
from conf import utils
from modules import module_interfaces
from modules import module_manager
from db import db_manager
import synchronize
from templates import template_manager

import class_forms

class Unknown_Module_in_DB(Exception):
  pass

class Formulaire:
  """
    Permet de générer tous les formulaires de l'administration
  """
  def __init__(self,mm,db,params,fields):
    self.mm=mm
    self.db=db
    self.params=params
    self.fields=fields
    self.page=class_forms.Content("","")
    self.errors={"incompleteFTP":_("Veuillez remplir tous les champs  concernant le serveur FTP."),
                 "incompleteTransferMode":_("Je ne sais pas comment vous avez pu réussir ça mais vous n'avez pas spécifié un mode de transfert correct. Soit vous êtes un hacker qui s'amuse, soit vous devriez remplir un rapport de bug."),
                 "incompleteSSH":_("Veuillez remplir tous les champs concernant le serveur SSH.")}
    
  def explore_dir_perso(self,options,root,prefix,extension_list):
    """    
      Crée les options du <select> HTML avec les pages persos
    """
    utils.mkdirp(os.path.join(root,prefix))
    pages=os.listdir(os.path.join(root,prefix))
    dirs=[]
    for p in pages:
      if os.path.isdir(os.path.join(root,prefix,p)):
        dirs.append(p)
      elif p[0]!=".":
        (path,ext)=os.path.splitext(p)        
        if extension_list==[]:
          item=os.path.join(prefix,p)
          options.append(([("value","0"+item)],item))              
        elif ext[1:] in extension_list:
          item=os.path.join(prefix,p)
          options.append(([("value","0"+item)],item))        
    for d in dirs: 
      if d[0]!=".":   
        self.explore_dir_perso(options,root,os.path.join(prefix,d),extension_list)


  def get_pages(self):
    """
      Renvoit la table "pages_perso"
      Champs:
      - page_id : string
      - page_title : string
      - page_wiki : string
      - pour chaque module M --> M_priority : int
    """
    return self.db.table(confstatic.pages_database_prefix).select(cond=[])



  def get_page(self,page_id):
    """
      Renvoit le ième élément de la table "pages_perso"
      Champs:
      - page_id : string
      - page_title : string
      - page_wiki : string
      - pour chaque module M --> M_priority : int
    """
    if page_id!="":
      return self.db.table(confstatic.pages_database_prefix). select(cond=[("page_id","=",page_id)]).next()
    else:
      new_page={"page_id": "", "page_title": "", "page_wiki": ""}
      modules=self.mm.get_available_modules()
      for m in modules:
        if isinstance(self.mm[m],module_interfaces.IModuleContentProvider):
          new_page[m+"_priority"]=-1
      index=0
      for m in confstatic.default_active_modules:
        new_page[m+"_priority"]=index
        index=index+1
      return new_page

  def get_module_priority(self,page,module):
    try:
      return page[module+"_priority"]
    except:
      raise Unknown_Module_in_DB(module)


  def gen_nav(self, page=False):
    titres = { "general"    : _("Général"),
               "pages"      : _("Pages"),
               "editpage"   : _("Édition du wiki"),
               "Educ"       : _("Enseignements"),
               "Calendars"  : _("Calendrier"),
               "News"       : _("News"),
               "Publi"      : _("Publications"),
               "Coord"      : _("Coordonnées"),
               "Menu"       : _("Menu"),
               "synchronize": _("Synchronisation"),
               "modpage"    : _("Modification d'une page") }
    nav_content=self.page.add_complex_option_tag("div",[("class","nav")])
    table=nav_content.add_complex_option_tag("table",[("width","100%"),("border","0")])
    cell1=(class_forms.Content("",""))
    cell1.add_link("admin.py", _("Configuration du site"))
    if self.params.has_key('from'):
      from_list = self.params['from'].split(',')
      from_prev = ''
      for f in from_list:
        cell1.add_text(' &gt; ')
        if from_prev != '':
          href = "?from=%s&amp;id=%s" % (from_prev, f)
          from_prev = from_prev + ',' + f
        else:
          href = "?id=%s" % f
          from_prev = f
        try:
          cell1.add_link(href, titres[f])
        except:
          cell1.add_link(href, f)
    if self.params.has_key('id'):
      try:
        titre = titres[self.params['id']]
      except:
        titre = self.params['id']
      cell1.add_text(' &gt; %s' % titre)

    if page and self.params.has_key('page_id'):
      cell2=(class_forms.Content("",""))
      cell2.add_link("handler.py?page="+self.params["page_id"]+".html", _("Aller à la page courante"))
    else:
      cell2=(class_forms.Content("",""))
      cell2.add_link("handler.py", _("Aller à l'accueil du site"))
    l = cell2.add_complex_option_tag("a", [("href","kill.py"), ("class", "kill")])
    l.add_complex_option_tag("img", [("src", "../styles/admin/kill.png"), ("style", "border-width: 0"),("alt",_("Arrêter le serveur")),("title",_("Arrêter le serveur"))])
    table.add_line([("td",[("align","left")],cell1),("td",[("align","right")],cell2)])


  def gen_form_main(self):
    """
      Page principale contenant les liens vers les formulaires.
    """
    title=_("CoMFoRT - Panneau d'administration")
    self.page = class_forms.Page(title,conf_general.style)
    title_content=self.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    self.gen_nav()
    
    body=self.page.add_complex_option_tag("div",[("class","body_class")])
    fieldset=body.add_complex_tag("fieldset")
    fieldset.add_simple_tag("legend",_("Configuration générale"))

    ul=fieldset.add_complex_tag("ul")

    li=ul.add_complex_tag("li")
    li.add_link("?id=general", _("Configuration du site"))
    li.add_complex_option_tag("div",[("class","info")]).add_text( _("Paramètres généraux du site : titre, langue, style, ..."))

    li=ul.add_complex_tag("li")
    li.add_link("?id=pages", _("Gestion des pages"))
    li.add_complex_option_tag("div",[("class","info")]).add_text( "Permet d'organiser les pages du site et leur contenu.") 

#    li=ul.add_complex_tag("li")
#    li.add_link("?id=pictures", _("Gestion des images"))
#    li.add_complex_option_tag("div",[("id","info")]).add_text("Permet de  #gérer la liste des images disponibles pour vos pages personnelles.") 

    body.add_br();
    fieldset=body.add_complex_tag("fieldset")
    fieldset.add_simple_tag("legend",_("Configuration des modules"))
    ul=fieldset.add_complex_tag("ul")
    admin_modules=filter(lambda m: isinstance(self.mm[m],module_interfaces.IModuleAdminPage), self.mm.get_available_modules())
    admin_modules.sort()
    for m in admin_modules:
      if not m==confstatic.module_credits_name:
        li=ul.add_complex_tag("li")
        li.add_link("?id="+m,self.mm[m].module_name())
        li.add_complex_option_tag("div",[("class","info")]).add_text(self.mm[m].module_admin_info())      

    if confstatic.mode=="local":
      body.add_br();
      fieldset=body.add_complex_tag("fieldset")
      fieldset.add_simple_tag("legend",_("Travail en local"))
      fieldset.add_simple_tag("p",_("Vous travaillez actuellement sur une copie locale du site")+".")

      ul=fieldset.add_complex_tag("ul")

      li=ul.add_complex_tag("li")
      li.add_link("?id=synchronize", _("Synchroniser"))
      li.add_complex_option_tag("div",[("class","info")]).add_text( _("Synchroniser les données de votre machine avec celles sur internet"))

    if self.mm.has_key(confstatic.module_credits_name):
      body.add_br();
      fieldset=body.add_complex_tag("fieldset")
      fieldset.add_simple_tag("legend",_("Crédits"))
      fieldset.add_simple_tag("p","CoMFoRT est un projet de la L3 section informatique de l'ENS Lyon - 2007/2008")
      ul=fieldset.add_complex_tag("ul")
      li=ul.add_complex_tag("li")
      li.add_link("?id="+confstatic.module_credits_name,self.mm[confstatic.module_credits_name].module_admin_info())
      
    self.gen_nav()




  def gen_form_install(self):
    """
      Formulaire d'installation
      Validation à effectuer: (via adminvalid.py?id=x)
      - id=install:
        *** Champs envoyés par POST ***
        *** A stocker dans ../conf/conf_general.py ***
        - title
        - language
        *** A stocker dans ../conf/conf_private.py ***
        - transfer_mode
        - server_ftp  (si transfer_mode == 'FTP')
        - user_ftp    (si transfer_mode == 'FTP')
        - root_ftp    (si transfer_mode == 'FTP')
      Erreur pouvant survenir: (via admin.py?id=install&amp;err=x)
      - err=incompleteFTP: Un des champs concernant la bdd est vide      
    """
    if conf_general.installed:
      self.gen_form_general()
      return
    else:
      title=_("Installation")
      self.page = class_forms.Page(title,conf_general.style)
      title_content=self.page.add_complex_option_tag("div",[("id","title")])
      title_content.add_text(title)
      if self.params.has_key("err"):
        if self.errors.has_key(self.params["err"]):
          error_content= self.page.add_complex_option_tag("div",[("class","error")])
          error_content.add_text(_("Erreur")+" : "+self.errors[self.params["err"]])

      form=self.page.add_form("adminvalid.py?id=install","post", id="method")

      body_content=form.add_complex_option_tag("div",[("class","body_class")])
      body=body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Paramètres du site"))
      table=body.add_table(0,0,3)
      table.add_line([("td",[("align","left")],class_forms.Text( _("Titre du site")+" : ")), ("td",[("align","left")],class_forms.Input("text","title", conf_general.title))])
      options=[]
      for l in confstatic.possible_languages:
        if conf_general.language==l[0]:
          options.append(([("value",l[0]),("selected","selected")],l[1]))
        else:
          options.append(([("value",l[0])],l[1]))
      table.add_line([("td",[("align","left")],class_forms.Text( _("Langue du site")+" : ")), ("td",[("align","left")],class_forms.Select("language",options))]) 

      optionspdf = []
      text = ""
      optionspdf.append(([("value","none"),("selected","selected")],_("Pas de génération de PDF")))
      if utils.java_ok():
        optionspdf.append(([("value","fop")],_("Avec FOP")))
      else:
        text += _("Impossible de trouver FOP : pas de génération de PDF avec FOP. ")
        text += _("Veuillez vous référer à la documentation pour l'installer.")
      if os.path.isfile(confstatic.dblatex_path()):
        optionspdf.append(([("value","latex")],_("Via LaTeX")))
      else:
        text += _("Impossible de trouver DBLatex : pas de génération de PDF avec DBLatex. ")
        text += _("Veuillez vous référer à la documentation pour l'installer.")
      table.add_line([("td",[("align","left")],class_forms.Text( _("Génération pdf ?")+" : ")), ("td",[("align","left")],class_forms.Select("pdfmode",optionspdf))]) 

      if confstatic.scp_path() != "":
        self.page.add_text("""
<script type="text/javascript">
function update_form() {
  var s = document.forms['method'].elements['transfer_mode'].value;
  switch(s) {
    case "FTP":
      document.getElementById('params_ssh').style.display = "none";
      document.getElementById('params_ftp').style.display = "block";
      break;
    case "SSH":
      document.getElementById('params_ftp').style.display = "none";
      document.getElementById('params_ssh').style.display = "block";
      break;
    default:
      alert("Ça ne devrait pas arriver...");
  }
}
update_form();
</script>
          """)

      table=body.add_table(0,0,3)
      if confstatic.scp_path() != "":
        options_transfer = [([("value", "FTP"), ("selected", "selected"),
                              ("onclick", "javascript:update_form()")], _("FTP")),
                            ([("value", "SSH"),
                              ("onclick", "javascript:update_form()")], _("SSH"))]
        table.add_line([("td",[("align","left")],class_forms.Text( _("Synchronisation distante")+" : ")), ("td",[("align","left")],class_forms.Select("transfer_mode",options_transfer,id="transfer_mode"))]) 
      else:
        table.add_input("hidden", "transfer_mode", "FTP")


      body=body_content.add_complex_option_tag("fieldset", [("id", "params_ftp")])
      body.add_simple_tag("legend",_("Paramètres FTP"))
      table=body.add_table(0,0,3)
      table.add_line([("td",[("align","left")],class_forms.Text( _("Serveur FTP")+" : ")), ("td",[("align","left")],class_forms.Input( "text","server_ftp",conf_private.server_ftp)) ])
      table.add_line([("td",[("align","left")],class_forms.Text( _("Login utilisateur")+" : ")), ("td",[("align","left")],class_forms.Input( "text","user_ftp",conf_private.user_ftp)) ])  
      table.add_line([("td",[("align","left")],class_forms.Text( _("Dossier racine du site")+" : ")),("td",[("align","left")], class_forms.Input("text","root_ftp",conf_private.root_ftp))])
      body.add_text(_("Par mesure de sécurité, le mot de passe FTP sera redemandé à chaque synchronisation (il pourra alors être enregistré par le gestionnaire de mot de passe de votre navigateur si vous ne désirez pas le ressaisir à chaque fois)."))

      if confstatic.scp_path != "":
        body=body_content.add_complex_option_tag("fieldset", [("id", "params_ssh")])
        body.add_simple_tag("legend",_("Paramètres SSH"))
        body.add_text(_("Par mesure de sécurité, l'adresse du serveur SSH sera redemandée à chaque synchronisation (il pourra alors être enregistré par le gestionnaire de mot de passe de votre navigateur si vous ne désirez pas le ressaisir à chaque fois)."))

      form.add_input("submit","submit",_("Finir l'installation"))


  def gen_form_general(self):
    """
      Formulaire pour les paramètres principaux
      Validation à effectuer: (via adminvalid.py?id=x)
      - id=general:
        *** Champs envoyés par POST ***
        *** A stocker dans ../conf/conf_general.py ***
        - title
        - language
    """
    title=_("Paramètres généraux")
    self.page = class_forms.Page(title,conf_general.style)
    title_content=self.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    self.gen_nav()

    form=self.page.add_form("adminvalid.py?id=general","post")

    body_content=form.add_complex_option_tag("div",[("class","body_class")])
    body=body_content.add_complex_tag("fieldset")
    body.add_simple_tag("legend",_("Paramètres du site"))
    table=body.add_table(0,0,3)
    table.add_line([("td",[("align","left")],class_forms.Text( _("Titre du site")+" : ")),("td",[("align","left")], class_forms.Input("text","title",conf_general.title))])

    options=[]
    for l in confstatic.possible_languages:
      if conf_general.language==l[0]:
        options.append(([("value",l[0]),("selected","selected")],l[1]))
      else:
        options.append(([("value",l[0])],l[1]))
    table.add_line([("td",[("align","left")],class_forms.Text( _("Langue du site")+" : ")), ("td",[("align","left")],class_forms.Select("language",options))])

    options=[]
    styles=os.listdir(os.path.join("styles","admin"))
    styles=filter (lambda s: os.path.isfile(os.path.join("styles","admin",s)) and s[0]!='.' and s.endswith(".css"), styles)
    for s in styles:
      if conf_general.adminstyle == s:
        options.append(([("selected","selected"),("value",s)],s))
      else:
        options.append(([("value",s)],s))
    table.add_line([("td",[("align","left")],class_forms.Text( _("Style de l'admin")+" : ")), ("td",[("align","left")],class_forms.Select("adminstyle",options))])

    styles=os.listdir("styles")
    styles=filter (lambda s: os.path.isdir(os.path.join("styles",s)) and s[0]!='.' and s != "common" and s != "admin", styles)
    catstyles = {}
    for s in styles:
      try:
        (cat, style) = s.split("_")
      except ValueError:
        (cat, style) = (_("Autres styles"), s)
      try:
        catstyles[cat]
      except KeyError:
        catstyles[cat] = []
      catstyles[cat].append(style)
    for c in catstyles:
      catstyles[c].sort()
    select = class_forms.Content("","").add_complex_option_tag("select", [("name", "style")])
    optgroups = []
    for c in catstyles:
      styles = catstyles[c]
      options = select.add_complex_option_tag("optgroup", [("label", c)])
      for s in styles:
        if c == _("Autres styles"):
          original_s = s
        else:
          original_s = c+"_"+s
        if conf_general.style==original_s:
          o = options.add_complex_option_tag("option", ([("value",original_s),("selected","selected")]))
          o.add_text(s)
        else:
          o = options.add_complex_option_tag("option", ([("value",original_s)]))
          o.add_text(s)
    table.add_line([("td",[("align","left")],class_forms.Text( _("Feuille de style à utiliser")+" : ")), ("td",[("align","left")],select)])

    optionspdf = []
    if conf_general.pdfmode == "none":
      optionspdf.append(([("value","none"),("selected","selected")],_("Pas de génération de PDF")))
    else:
      optionspdf.append(([("value","none")],_("Pas de génération de PDF")))
    if utils.java_ok(): 
      if conf_general.pdfmode == "fop":
          optionspdf.append(([("value","fop"),("selected","selected")],_("Avec FOP")))
      else:
          optionspdf.append(([("value","fop")],_("Avec FOP")))
    if os.path.isfile(confstatic.dblatex_path()):
      if conf_general.pdfmode == "latex":
          optionspdf.append(([("value","latex"),("selected","selected")],_("Via LaTeX")))
      else:
          optionspdf.append(([("value","latex")],_("Via LaTeX")))
    table.add_line([("td",[("align","left")],class_forms.Text( _("Génération pdf ?")+" : ")), ("td",[("align","left")],class_forms.Select("pdfmode",optionspdf))]) 


    #if confstatic.mode=='dynamic':
    if False: ## Is not used ! It is not taken into account by generation of
              ## conf_general.py and it makes the bug under apache
              #ne sert pas !!!, n'est pas pris en compte par la génération de
              #conf_general.py et fait beuguer le site sous apache
      body.add_link("admin.py?id=pass","Changer le mot de passe administrateur")   

      form.add_br();
      body_content=form.add_complex_option_tag("div",[("class","body_class")])
      body=body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Paramètres base de données"))
      table=body.add_table(0,0,3)
      table.add_line([("td",[("align","left")],class_forms.Text( _("Serveur de la base de données")+" : ")), ("td",[("align","left")],class_forms.Input( "text","server_db",conf_general.server_db)) ])
      table.add_line([("td",[("align","left")],class_forms.Text( _("Login utilisateur")+" : ")), ("td",[("align","left")],class_forms.Input( "text","user_db",conf_general.user_db)) ])      
      table.add_line([("td",[("align","left")],class_forms.Text( _("Mot de passe")+" : ")), ("td",[("align","left")],class_forms.Input( "password","pass_db",conf_general.pass_db)) ])
      table.add_line([("td",[("align","left")],class_forms.Text( _("Nom de la base de données")+" : ")), ("td",[("align","left")],class_forms.Input( "text","name_db",conf_general.name_db)) ])

    form.add_input("submit","submit",_("Appliquer"))

    self.gen_nav()



## Not used anymore
# N'est plus utilisé
#  def gen_form_pass(self):
#    """
#      Formulaire pour les paramètres principaux
#      Validation à effectuer: (via adminvalid.py?id=x)
#      - id=pass:
#        *** Champs envoyés par POST ***
#        *** A stocker dans ../conf/conf_general.py ***
#        - last_pass
#        - new_pass
#        - conf_pass
#      Erreur pouvant survenir: (via admin.py?id=pass&amp;err=x)
#      - err=emptyPass : le nouveau mot de passe est vide
#      - err=incorrectPass: l'ancien mot de passe n'est pas le bon
#      - err=incorrectConf: le nouveau mot de passe et la confirmation sont
#                           différents      
#    """
#    title=_("Changement du mot de passe administrateur")
#    self.page = class_forms.Page(title,conf_general.style)
#    title_content=self.page.add_complex_option_tag("div",[("id","title")])
#    title_content.add_text(title)
#
#    self.gen_nav()
#
#    if self.params.has_key("err"):
#      errors={ "emptyPass"    :_("Veuillez indiquez un mot de passe."), "incorrectPass":_("L'ancien mot de passe est incorrect."), #"incorrectConf":_("Le nouveau mot de passe et la confirmation sont différents.")}
#      if errors.has_key(self.params["err"]):
#        self.page.add_br();
#        error_content=self.page.add_complex_option_tag("div",[("class","error")])
#        error_content.add_text(_("Erreur")+" : "+errors[self.params["err"]])
#
#    self.page.add_br();
#    form=self.page.add_form("adminvalid.py?id=pass","post")
#
#    body_content=form.add_complex_option_tag("div",[("class","body_class")])
#    body=body_content.add_complex_tag("fieldset")
#    table=body.add_table(0,0,3)
#    table.add_line([("td",[("align","left")], class_forms.Text(_("Ancien mot de passe")+" : ")), ("td",[("align","left")], #class_forms.Input("password","last_pass",""))])
#    table.add_line([("td",[("align","left")], class_forms.Text(_("Nouveau mot de passe")+" : ")), ("td",[("align","left")], #class_forms.Input("password","new_pass",""))])  
#    table.add_line([("td",[("align","left")], class_forms.Text(_("Confirmation mot de passe")+" : ")), ("td",[("align","left")], #class_forms.Input("password","conf_pass",""))])
#    form.add_input("submit","submit",_("Appliquer"))
#
#    self.gen_nav()



  def gen_form_pages(self):
    """
      Formulaire de gestion des pages   
    """    
    title=_("Gestion des pages")
    self.page = class_forms.Page(title,conf_general.style)
    title_content=self.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    self.gen_nav();

    body_content=self.page.add_complex_option_tag("div",[("class","body_class")])
    body=body_content.add_complex_tag("fieldset")
    body.add_simple_tag("legend",_("Liste des pages"))
    body.add_simple_tag("p",_("Voici la liste des pages du site:"))

    ## Existing personal pages retrieved
    # On récupère les pages perso existantes
    pages=self.get_pages()

    if len(pages)==0:
      body.add_simple_tag("p",_("Erreur imprévue: Il n'y a aucune page  personnelle. Veuillez créer une page nommée \"")+confstatic.default_page_name+"\".")
    else: 
      table = body.add_table(1,0,3)

      table.add_line([("th",[("align","center")],class_forms.Text( "ID de la page")), ("th",[("align","center")],class_forms.Text( "Titre de la page")), ("th",[("align","center")],class_forms.Text(\
"Actions")) ])
      
      for p in pages:
        buttons=(class_forms.Content("","")).add_table(0,0,3)

        form1=(class_forms.Content("","")).add_form( """admin.py?from=pages&amp;id=modpage&amp;page_id=%s"""%(urllib.quote(p["page_id"])),"post")
        form1.add_input("submit","submit", _("Configurer"))

        form2=(class_forms.Content("","")).add_form( """admin.py?from=pages&amp;id=editpage&amp;page_id=%s"""%(urllib.quote(p["page_id"])),"post")
        opt=[("type","submit"),("name","submit"),("value",_("Éditer Wiki"))]
        if self.get_module_priority(p,confstatic.module_wiki_name)==-1:
          opt.append(("disabled","disabled"))
        form2.add_single_tag("input",opt)

        form3=(class_forms.Content("","")).add_form( """admin.py?from=pages&amp;id=delpage&amp;page_id=%s"""%(urllib.quote(p["page_id"])),"post")
        opt=[("type","submit"),("name","submit"),("value", _("Supprimer"))]
        if p["page_id"]==confstatic.default_page_name:
          opt.append(("disabled","disabled"))
        form3.add_single_tag("input",opt)  

        buttons.add_line([("td",[],form1), ("td",[],form2), ("td",[],form3)])

        table.add_line([ ("td",[("align","center")],class_forms.Text(p["page_id"])), ("td",[("align","left")],class_forms.Text(p["page_title"])), ("td",[("align","left")],buttons)])

    form=body.add_form("admin.py?from=pages&amp;id=modpage&amp;page_id=","post")
    p=form.add_complex_tag("p")
    p.add_input("submit","submit", _("Créer une nouvelle page"))

    self.gen_nav()



  def gen_form_delpage(self):
    """
      Formulaire pour confirmer la suppression d'une page
      Validation a effectuer: (via adminvalid.py?id=x) 
      - id=page_del: Supprimer le boutton page_id
        *** Champs envoyés par POST ***
        *** A stocker dans la BDD, table: "pages" ***
        - page_id
    """
    ## id of the item to modify
    #id de l'item a modifier
    if self.params.has_key("page_id"):
      title=_("Suppression d'une page")
      self.page = class_forms.Page(title,conf_general.style)
      title_content=self.page.add_complex_option_tag("div",[("id","title")])
      title_content.add_text(title)

      self.gen_nav(page=True)

      body_content=self.page.add_complex_option_tag("div",[("class","body_class")])
      body=body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Confirmation de suppression de la page")+" \""+urllib.unquote(self.params["page_id"]+"\""))
      p=body.add_complex_tag("p")
      p.add_text(_("Confirmez-vous la suppression de la page")+" \""+urllib.unquote(self.params["page_id"])+ "\"? "+_("Attention cette opération est irréversible!"))
      form = body.add_form("adminvalid.py?from=pages&amp;id=page_del", "post")
      form.add_input("hidden","page_id",urllib.unquote(self.params["page_id"]))
      ##warning: in valid_forms.py
      ##the value _("Supprimer") is used
      #attention: dans valid_forms.py
      #la valeur _("Supprimer") est utilisée
      #penser à faire correspondre la chaîne ci-dessous avec
      #celle de valid_forms.py
      form.add_input("submit", "submit", _("Supprimer"))  

      #form = body.add_form("admin.py?id=pages", "post")
      form.add_input("submit", "submit", _("Annuler"))

      self.gen_nav(page=True)
    else:
      self.gen_form_pages()
      return



  def gen_form_modpage(self):
    """
      Formulaire pour modifier une page
      Validation a effectuer: (via adminvalid.py?id=x) 
      - id=page_edit: Mettre a jour la page page_id
        *** Champs envoyés par POST ***
        *** A stocker dans la BDD, table: "pages" ***
        - page_id
        - page_title
        - new_page: 0 ou 1
        - action: up, down, edit_wiki ou active_wiki
        - module: le module concerné par l'action
      Erreur pouvant survenir: (via admin.py?id=modpage&amp;err=x)
      - err=existsID : une image portant le même nom existe déjà
      - err=emptyID : ID vide: c'est interdit
    """
    if self.params.has_key("page_id"):
      ## Get back all the information in the database
      # Recuperer toutes les infos dans la bdd
      try:
        page=self.get_page(urllib.unquote(self.params["page_id"]))
      except:
        self.gen_form_pages()
        return
      ##
      # Fin info bdd 
      if self.params["page_id"]=="":
        title=_("Ajout d'une page")
      else:
        title=_("Modification de la page")+" \""+self.params["page_id"]+"\": "+page["page_title"]
      self.page = class_forms.Page(title,conf_general.style)
      
      title_content=self.page.add_complex_option_tag("div",[("id","title")])
      title_content.add_text(title)

      self.gen_nav(page=True)
      
      js_content=self.page.add_complex_option_tag("div",[("id","activ_js")])
      js_content.add_text(_("Pour que cette page fonctionne correctement, vous devez activer le JavaScript."))   
      
      self.page.add_text( """<script language=\"javascript\" type=\"text/javascript\">
/* <![CDATA[ */
div=document.getElementById('activ_js');
div.removeChild(div.firstChild);
function submit_form(module,action){
document.getElementById('forme').module.value=module;
document.getElementById('forme').action.value=action;
document.getElementById('forme').submit();
}
/* ]]> */
</script>""")      
                
      if self.params.has_key("err"):
        errors={ "emptyID"    :_("Veuillez indiquer un ID non vide pour la page."),
            "existsID":_("Le nouvel ID est déjà utilisé."),
            "badID":_("L'identifiant utilisé contient des caractères accentués ou non-alphanumériques")}
        if errors.has_key(self.params["err"]):
          error_content=self.page.add_complex_option_tag("div",[("class","error")])
          error_content.add_text(_("Erreur")+" : "+errors[self.params["err"]])
          
      form = self.page.add_complex_option_tag("form",[ ("action","adminvalid.py?id=page_edit"),("method","post"),("id","forme")])
      form.add_input("hidden","last_id",page["page_id"])
      form.add_input("hidden","module","")
      form.add_input("hidden","action","")

      body_content=form.add_complex_option_tag("div",[("class","body_class")])
      body=body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Paramètres de la page"))
      table = body.add_table(0,0,3)
      ## Welcoming page ID cannot be modified
      #On ne peut pas modifier l'ID de la page d'accueil
      if(page["page_id"]==confstatic.default_page_name):
        c=class_forms.Content("","")
        c.add_single_tag("input",[ ("type","text"), ("value",page["page_id"]), ("disabled","disabled")])
        form.add_input("hidden","page_id",page["page_id"])
        table.add_line([ ("td",[("align","left")],class_forms.Text( _("Identifiant propre à la page")+" : ")), ("td",[("align","left")],c)])
        table.add_line([ ("td",[("align","left")],class_forms.Text(_("Titre de la page")+" : ")), ("td",[("align","left")],class_forms.Input("text","page_title",page["page_title"]))])

        styles=os.listdir("styles")
        styles=filter (lambda s: os.path.isdir(os.path.join("styles",s)) and s[0]!='.' and s != "common" and s != "admin", styles)
        catstyles = {}
        for s in styles:
          try:
            (cat, style) = s.split("_")
          except ValueError:
            (cat, style) = (_("Autres styles"), s)
          try:
            catstyles[cat]
          except KeyError:
            catstyles[cat] = []
          catstyles[cat].append(style)
        for c in catstyles:
          catstyles[c].sort()
        select = class_forms.Content("","").add_complex_option_tag("select", [("name", "page_style")])
        optgroups = []
        for c in catstyles:
          styles = catstyles[c]
          options = select.add_complex_option_tag("optgroup", [("label", c)])
          for s in styles:
            if c == _("Autres styles"):
              original_s = s
            else:
              original_s = c+"_"+s
            if (page["page_style"] == None and conf_general.style==original_s) or page["page_style"] == original_s:
              o = options.add_complex_option_tag("option", ([("value",original_s),("selected","selected")]))
              o.add_text(s)
            else:
              o = options.add_complex_option_tag("option", ([("value",original_s)]))
              o.add_text(s)
        table.add_line([("td",[("align","left")],class_forms.Text( _("Feuille de style propre à cette page")+" : ")), ("td",[("align","left")],select)])

       
      else:
        table.add_line([ ("td",[("align","left")],class_forms.Text( _("Identifiant propre à la page")+" : ")), ("td",[("align","left")],class_forms.Input("text","page_id",page["page_id"]))])      
        table.add_line([ ("td",[("align","left")],class_forms.Text(_("Titre de la page")+" : ")), ("td",[("align","left")],class_forms.Input("text","page_title",page["page_title"]))])
        ## Checking whether page is in the menu. If it is not, suggest to add it
        #on vérifie si la page est dans le menu ou non... si non, on propose de l'ajouter
        in_menu=True 
        try:
          table_db = self.db.table(self.mm[confstatic.module_menu_name].database_prefix+"_items")
          try:
            table_db.select(cond=[("item_link","=",self.params["page_id"])]).next()
          except:
            in_menu=False
        except:
          pass
        if not in_menu:        
          table.add_line([ ("td",[("align","left")],class_forms.Text( _("Ajouter un bouton au menu")+" : ")), ("td",[("align","left")],class_forms.Input("checkbox","page_addmenu", ""))])

      body_content=form.add_complex_option_tag("div",[("class","body_class")])
      body=body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Modules de la page"))
      body.add_simple_tag("p",_("Voici la liste des modules apparaîssant sur la page. Ils sont  classés par ordre d'apparition:"))

      table = body.add_table(1,0,3)
      table.add_line([ ("th",[("align","center")],class_forms.Text(_("Module"))), ("th",[("align","center")],class_forms.Text(_("Activation du module"))), ("th",[("align","center")],class_forms.Text(_("Action")))])

      def make_select_activation(module):
        options=[([("value","1")],"activé"),([("value","0")],"désactivé")]        
        if self.get_module_priority(page,module)!=-1:
          options[0][0].append(("selected","selected"))
        else:
          options[1][0].append(("selected","selected"))
        select=(class_forms.Content("","")).add_complex_option_tag("select", [("name",module+"_state"),("onchange","javascript:submit_form('%s','refresh')" %(module))])
        for o in options:
          opt=select.add_complex_option_tag("option",o[0])
          opt.add_text(o[1])
        return select

      def make_buttons(priority,module,up,down):
        if(priority>-1):
          c=class_forms.Content("","")
          opt=[("type","button"),("value",_("Monter")), ("onclick","javascript:submit_form('"+module+"','up')")]
          if not up:
            opt.append(("disabled","disabled"))
          c.add_single_tag("input",opt)
          opt=[("type","button"),("value",_("Descendre")), ("onclick","javascript:submit_form('"+module+"','down')")]
          if not down:
            opt.append(("disabled","disabled"))
          c.add_single_tag("input",opt)
          return c
        else:
          c = class_forms.Content("","")
          c.add_text(_("module inactif"))
          return c

      modules=filter(lambda m: isinstance(self.mm[m], module_interfaces.IModuleContentProvider), self.mm.get_available_modules())
      modules_priority=[]
      count=0;
      for m in modules:
        priority=self.get_module_priority(page,m)
        modules_priority.append((priority,m))
        if priority!=-1: count=count+1       
      modules_priority.sort()
      modules_priority.reverse()
      for m in modules_priority:
        body.add_input("hidden",m[1]+"_priority",str(m[0]))
        table.add_line([ ("td",[("align","center")],class_forms.Text(self.mm[m[1]].module_name())), ("td",[("align","center")],make_select_activation(m[1])), ("td",[("align","center")],make_buttons(m[0],m[1],m[1]!=modules_priority[0][1] and count>0,count>1))])
        count=count-1

      if self.get_module_priority(page,confstatic.module_wiki_name)!=-1:
        p=body.add_complex_tag("p")
        p.add_text(_("Wiki activé")+" : ")
        p.add_br()
        p.add_single_tag("input",[("type","button"),("value",_("Éditer le  texte de la page.")),("onclick","javascript:submit_form('','edit_wiki')")])
      else:
        p=body.add_complex_tag("p")
        p.add_text(_("Le module wiki est désactivé: vous ne pouvez pas éditer le texte de la page."))
        p.add_br()
        p.add_single_tag("input",[("type","button"),("value",_("Activer le  wiki pour cette page.")),("onclick","javascript:submit_form('','active_wiki')")])
      form.add_input("submit", "apply", _("Appliquer"))

      self.gen_nav(page=True)
    else:
      self.gen_form_pages()
      return


  def gen_form_editpage(self):
    """
      Formulaire d'édition du wiki
      Validation a effectuer: (via adminvalid.py?id=x&amp;page='page')
      *** A stocker dans la BDD, table: "pages" ***
      - id=page_wiki: Sauve le texte dans la BD
        *** Champs envoyes par POST ***
        - page_id
        - page_wiki
    """
    if self.params.has_key("page_id"):

      page=self.get_page(urllib.unquote(self.params["page_id"]))

      title=_("Édition de la page \""+self.params["page_id"]+"\": "+page["page_title"])
      self.page = class_forms.Page(title,conf_general.style)

      title_content=self.page.add_complex_option_tag("div",[("id","title")])
      title_content.add_text(title)

      self.gen_nav(page=True)
      
      js_content=self.page.add_complex_option_tag("div",[("id","activ_js")])
      js_content.add_text(_("Pour que cette page fonctionne correctement, vous devez activer le JavaScript."))

      wiki_string=None
      if self.params.has_key("apercu"):
        if self.params["apercu"]=="1":
          try:
            fp=open(confstatic.overview_path,"r")
            wiki_string=fp.read()
            fp.close()
            os.remove(confstatic.overview_path)
            body_content=self.page.add_complex_option_tag("div",[("class","apercu")])
            body=body_content.add_complex_tag("fieldset")
            body.add_simple_tag("legend",_("Aperçu"))  
            tm = template_manager.TemplateManager(self.db,self.params["page_id"], None)
            body.add_text(tm.generate_wiki_xhtml(wiki_string))  
          except:
            pass
            
      form = self.page.add_complex_option_tag("form",[ ("action","adminvalid.py?id=page_wiki"),("method","post"),("id","forme")])
      form.add_input("hidden","page_id",self.params["page_id"])
      body_content=form.add_complex_option_tag("div",[("class","body_class")])
      body=body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Texte wiki"))

      table=body.add_table(0,0,0)      
      cell1=class_forms.Content("","")
            
      path="../interface/images"
      def add_btn(btn,hint):
        cell1.add_single_tag("img",[("class","wiki_btn"),\
                                   ("src",path+"/button_"+btn+".png"),\
                                   ("title",hint),\
                                   ("alt",btn),\
                                   ("onclick","javascript: btn_"+btn+"()")])

      add_btn("italic",_("Texte italique"))             
      add_btn("bold",_("Texte gras"))
      add_btn("underline",_("Texte souligné"))      
      add_btn("strike",_("Texte barré"))          
      add_btn("headline",_("Titre de second niveau")) 
      add_btn("link",_("Lien interne"))  
      add_btn("extlink",_("Lien externe"))   
      add_btn("image",_("Image"))             
      add_btn("math",_("Formule mathématique (LaTeX)"))  
      add_btn("nowiki",_("Texte préformaté"))  
      add_btn("array",_("Tableau"))   
      add_btn("liste",_("Liste non ordonnée"))  
      add_btn("enum",_("Liste ordonnée"))  
      add_btn("ref",_("Note de bas de page"))                                       
      cell1.add_br()
      textarea=cell1.add_complex_option_tag("textarea",[("name","page_wiki"),("id","page_wiki"),("rows","25"),("cols","80")])
            
      cell2=class_forms.Content("","")
      div=cell2.add_complex_option_tag("div",[("class","selects")])
      div.add_simple_tag("b","Insérer un lien vers une page:")      
      div.add_br()
      select=div.add_complex_option_tag("select",[("id","insert_page_link"),("onclick","Javascript: add_page_link()")])      
      options=[([("selected","selected"),("value","")],_("--- Insérer un lien vers une page ---"))]
      options.append(([("disabled","disabled"),("value","")],_("** Page externe à CoMFoRT **")))  
      options.append(([("value","ext")],_("Insérer un lien vers une page externe...")))    
      options.append(([("disabled","disabled"),("value","")],_("** Pages gérées par CoMFoRT **")))               
      pages=self.db.table(confstatic.pages_database_prefix).select(cond=[])
      for p in pages:      
        options.append(([("value","1"+p["page_id"])],p["page_id"]))  
      options.append(([("disabled","disabled"),("value","")],_("** Pages personnelles (perso/pages) **")))         
      self.explore_dir_perso(options,os.path.join(confstatic.config_path,"perso","pages"),"",confstatic.pages_perso_extensions)              
      for o in options:
        opt=select.add_complex_option_tag("option",o[0])
        opt.add_text(o[1])

      div.add_br()
      div.add_br()      
      div.add_simple_tag("b","Insérer une image:")      
      div.add_br()
      select=div.add_complex_option_tag("select",[("id","insert_image"),("onclick","Javascript: add_image()")])      
      options=[([("selected","selected"),("value","")],_("--- Insérer une image ---"))]
      options.append(([("disabled","disabled"),("value","")],_("** Image externe à CoMFoRT **")))  
      options.append(([("value","ext")],_("Insérer une image externe...")))
      options.append(([("disabled","disabled"),("value","")],_("** Images personnelles (perso/pictures) **")))        
      self.explore_dir_perso(options,os.path.join(confstatic.pictures_path),"",[])  
      for o in options:
        opt=select.add_complex_option_tag("option",o[0])
        opt.add_text(o[1])              

      div.add_br()
      div.add_br()
      div.add_simple_tag("b","Insérer un lien vers une image perso:")      
      div.add_br()
      select=div.add_complex_option_tag("select",[("id","insert_image_link"),("onclick","Javascript: add_image_link()")])      
      options=[([("selected","selected"),("value","")],_("--- Insérer un lien vers une image ---"))]
      self.explore_dir_perso(options,os.path.join(confstatic.pictures_path),"",[])  
      for o in options:
        opt=select.add_complex_option_tag("option",o[0])
        opt.add_text(o[1])  
                    
      div.add_br()
      div.add_br()      
      div.add_simple_tag("b","Insérer un lien vers un document perso:")      
      div.add_br()
      select=div.add_complex_option_tag("select",[("id","insert_doc_link"),("onclick","Javascript: add_doc_link()")])      
      options=[([("selected","selected"),("value","")],_("--- Insérer un lien vers un document ---"))]
      self.explore_dir_perso(options,os.path.join(confstatic.config_path,"perso","docs"),"",[])  
      for o in options:
        opt=select.add_complex_option_tag("option",o[0])
        opt.add_text(o[1])
        
      div.add_br()
      div.add_br()      
      div.add_simple_tag("b","Insérer le contenu d'un module:")      
      div.add_br()
      select=div.add_complex_option_tag("select",[("id","insert_module"),("onclick","Javascript: add_module()")])      
      options=[([("selected","selected"),("value","")],_("--- Insérer le contenu d'un module ---"))]
      content_modules=filter(lambda m: isinstance(self.mm[m], module_interfaces.IModuleContentProvider), self.mm.get_available_modules())
      for m in content_modules:
        if m!=confstatic.module_wiki_name and m!=confstatic.module_menu_name:
          options.append(([("value",m)],self.mm[m].module_name()))  
      for o in options:
        opt=select.add_complex_option_tag("option",o[0])
        opt.add_text(o[1])                                 
                                   
      
      table.add_line([("td",[("width","100%")],cell1),("td",[],cell2)])
      if wiki_string!=None:
        textarea.add_text("\n"+wiki_string)
      elif page["page_wiki"]!=None:
        textarea.add_text(page["page_wiki"])

      body.add_input("submit","submit", _("Aperçu"))
      form.add_input("submit","submit", _("Appliquer"))

      self.gen_nav(page=True)

      self.page.add_text( """<script language=\"javascript\" type=\"text/javascript\">
/* <![CDATA[ */

div=document.getElementById('activ_js');
div.removeChild(div.firstChild);

function insert(l, texte, r)
{
  textarea=document.getElementById('page_wiki');
  text=textarea.value;
  i=textarea.selectionStart;
  left=text.substr(0,i);
  middle=text.substr(i,textarea.selectionEnd-i);
  right=text.substr(textarea.selectionEnd,text.length-textarea.selectionEnd); 
  if(middle=="") {  
    textarea.value=left+l+texte+r+right;
    textarea.setSelectionRange(i+l.length,i+l.length+texte.length);    
  }
  else {
    textarea.value=left+l+middle+r+right;
    textarea.setSelectionRange(i+l.length,i+l.length+middle.length);    
  }
  textarea.focus()
}

function insert_before(texte)
{
  textarea=document.getElementById('page_wiki');
  text=textarea.value
  i=textarea.selectionStart
  left=text.substr(0,i);
  right=text.substr(i,text.length-i); 
  textarea.value=left+texte+right;
  textarea.focus()  
}

function btn_bold()     {insert("'''", \"%s\", "'''");} 
function btn_italic()   {insert("''", \"%s\", "''");}
function btn_underline(){insert("<u>", \"%s\", "</u>");}
function btn_strike()   {insert("<s>", \"%s\", "</s>");}
function btn_headline() {insert("== ", \"%s\", " ==");} 
function btn_link()     {insert("[[", \"%s\", "]]");} 
function btn_extlink()  {insert("[", \"%s\", "]");} 
function btn_image()    {insert("[[Image:", \"%s\", "]]");} 
function btn_math()     {insert("<math size=\\\"%s\\\" packages=\\\"\\\">", \"%s\", "</math>");} 
function btn_nowiki()   {insert("<nowiki>", \"%s\", "</nowiki>");}
function btn_array()    {insert_before(\"%s\");}
function btn_liste()    {insert_before(\"%s\");}
function btn_enum()     {insert_before(\"%s\");}
function btn_ref()      {insert("<ref>", \"%s\", "</ref>");}

function add_page_link()
{
  select=document.getElementById('insert_page_link');
  if(select.value=="") 
    return;
  else if(select.value=="ext")
    insert("[", \"%s\", "]");
  else {
    val=select.value.substr(1,select.value.length)
    if(select.value.substr(0,1)=='1')
      insert_before("[["+val+"]]");
    else 
      insert_before("[[Page:"+val+"]]"); 
  }    
  select.selectedIndex=0;
}
function add_image()
{
  select=document.getElementById('insert_image');
  if(select.value=="") 
    return;
  else if(select.value=="ext")
    insert("[Image:", \"%s\", "]");
  else {
    val=select.value.substr(1,select.value.length)
    insert_before("[[Image:"+val+"]]"); 
  }          
  select.selectedIndex=0;
}
function add_image_link()
{
  select=document.getElementById('insert_image_link');
  if(select.value=="") 
    return;  
  else {
    val=select.value.substr(1,select.value.length)
    insert_before("[[Picture:"+val+"]]"); 
  }     
  select.selectedIndex=0;
}
function add_doc_link()
{
  select=document.getElementById('insert_doc_link');
  if(select.value=="") 
    return;  
  else {
    val=select.value.substr(1,select.value.length)
    insert_before("[[Doc:"+val+"]]"); 
  }        
  select.selectedIndex=0;
}
function add_module()
{
  select=document.getElementById('insert_module');
  if(select.value=="") 
    return;  
  else
    insert_before("<module id=\\\""+select.value+"\\\" params=\\\"\\\" />");      
  select.selectedIndex=0;
}
/* ]]> */
</script>"""
%(_("Texte gras"),\
  _("Texte italique"),\
  _("Texte souligné"),\
  _("Texte barré"),\
  _("Texte de titre"),\
  _("Lien interne"),\
  _("Lien externe"),\
  _("exemple.jpg"),\
  confstatic.default_latex_dpi,\
  _("Entrez votre formule ici"),\
  _("Entrez le texte non formaté ici"),\
  "{|\\n|-\\n|\\n|\\n|}",\
  _("* élément A\\n* élément B\\n* élément C"),\
  _("# élément 1\\n# élément 2\\n# élément 3"),\
  _("référence ou citation"),\
  _("Lien externe"),\
  _("Exemple.jpg")
))  

    else:
      self.gen_form_pages()
      return




  def gen_form_synchronize(self):
    """
      Formulaire pour (éventuellement) confirmer la synchronisation
      Validation à effectuer: (via admin.py?id=synchronize)

                       ! ! ! ATTENTION ! ! !
      L'action effectuée après ce formulaire (la synchronisation)
      est inhabituellement longue, elle ne peut donc être effectuée
      par adminvalid sans retour utilisateur, d'où l'appel à admin.py.
      Ne pas suivre cet exemple !

      Erreur pouvant survenir: (via admin.py?id=install&amp;err=x)
      - err=incompleteTransferMode: Un des champs concernant la bdd est vide      
      - err=incompleteFTP: Un des champs concernant la bdd est vide      
      - err=incompleteSSH: Un des champs concernant la bdd est vide      
    """
    title=_("Synchronisation")
    self.page = class_forms.Page(title,conf_general.style)
    title_content=self.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    self.gen_nav()

    valid_transfer_mode = self.fields.has_key("transfer_mode") and self.fields["transfer_mode"].value in ["FTP", "SSH"]
    valid_ftp = valid_transfer_mode and self.fields["transfer_mode"].value == "FTP" and \
                self.fields.has_key("server_ftp") and self.fields["server_ftp"].value != "" and \
                self.fields.has_key("user_ftp") and self.fields["user_ftp"].value != "" and \
                self.fields.has_key("pass_ftp") and self.fields["pass_ftp"].value != ""
    valid_ssh = valid_transfer_mode and self.fields["transfer_mode"].value == "SSH" and \
                self.fields.has_key("server_ssh") and self.fields["server_ssh"].value != ""

    if not valid_transfer_mode or not valid_ftp and not valid_ssh:
      if self.fields.has_key("transfer_mode"):
        if not valid_transfer_mode:  # je vois mal comment ça pourrait arriver, mais bon autant être prudent
          error_content= self.page.add_complex_option_tag("div",[("class","error")])
          error_content.add_text(_("Erreur")+" : "+self.errors["incompleteTransferMode"])
        elif self.fields["transfer_mode"].value == "FTP" and not valid_ftp:
          error_content= self.page.add_complex_option_tag("div",[("class","error")])
          error_content.add_text(_("Erreur")+" : "+self.errors["incompleteFTP"])
        elif not valid_ssh:
          error_content= self.page.add_complex_option_tag("div",[("class","error")])
          error_content.add_text(_("Erreur")+" : "+self.errors["incompleteSSH"])

      if confstatic.scp_path() != "":
        self.page.add_text("""
<script type="text/javascript">
function update_form() {
  var s = document.forms['method'].elements['transfer_mode'].value;
  switch(s) {
    case "FTP":
      document.getElementById('params_ssh').style.display = "none";
      document.getElementById('params_ftp').style.display = "block";
      break;
    case "SSH":
      document.getElementById('params_ftp').style.display = "none";
      document.getElementById('params_ssh').style.display = "block";
      break;
    default:
      alert("Ça ne devrait pas arriver...");
  }
}
var body = document.getElementsByTagName("body")[0];
body.addEventListener("load", update_form, true);
</script>
          """)
      form=self.page.add_form("admin.py?id=synchronize","post", id="method")

      body_content=form.add_complex_option_tag("div",[("class","body_class")])

      body=body_content.add_complex_option_tag("fieldset", [("id", "params_general")])
      body.add_simple_tag("legend",_("Paramètres généraux"))
      table=body.add_table(0,0,3)
      if confstatic.scp_path() != "":
        options_transfer = []
        if conf_private.transfer_mode == "FTP":
          options_transfer.append(([("value", "FTP"), ("selected", "selected"),
                                    ("onclick", "javascript:update_form()")
                                   ], _("FTP")))
        else:
          options_transfer.append(([("value", "FTP"),
                                    ("onclick", "javascript:update_form()")
                                   ], _("FTP")))
        if conf_private.transfer_mode == "SSH":
          options_transfer.append(([("value", "SSH"), ("selected", "selected"),
                                    ("onclick", "javascript:update_form()")
                                   ], _("SSH")))
        else:
          options_transfer.append(([("value", "SSH"),
                                    ("onclick", "javascript:update_form()")
                                   ], _("SSH")))
      else:
        table.add_input("hidden", "transfer_mode", "FTP")
      table.add_line([("td",[("align","left")],class_forms.Text( _("Synchronisation distante")+" : ")), ("td",[("align","left")],class_forms.Select("transfer_mode",options_transfer))]) 


      body=body_content.add_complex_option_tag("fieldset", [("id", "params_ftp")])
      body.add_simple_tag("legend",_("Paramètres FTP"))
      table=body.add_table(0,0,3)
      table.add_line([("td",[("align","left")],class_forms.Text( _("Serveur FTP")+" : ")), ("td",[("align","left")],class_forms.Input( "text","server_ftp",conf_private.server_ftp)) ])
      table.add_line([("td",[("align","left")],class_forms.Text( _("Login utilisateur")+" : ")), ("td",[("align","left")],class_forms.Input( "text","user_ftp",conf_private.user_ftp)) ])  
      table.add_line([("td",[("align","left")],class_forms.Text( _("Mot de passe")+" : ")), ("td",[("align","left")],class_forms.Input( "password","pass_ftp","")) ])
      table.add_line([("td",[("align","left")],class_forms.Text( _("Dossier racine du site")+" : ")),("td",[("align","left")], class_forms.Input("text","root_ftp",conf_private.root_ftp))])

      if confstatic.scp_path != "":
        body=body_content.add_complex_option_tag("fieldset", [("id", "params_ssh"), ("onload", "javascript:update_form()")])
        body.add_simple_tag("legend",_("Paramètres SSH"))
        table=body.add_table(0,0,3)
        table.add_line([("td",[("align","left")],class_forms.Text( _("Serveur SSH")+" : ")),("td",[("align","left")], class_forms.Input("text","server_ssh",""))])

      form.add_input("submit","submit",_("Synchroniser"))
      if os.name == 'nt':
        form.add_text(_("(Attention : ceci peut prendre plusieurs minutes.)"))  # le sys.stdout.flush ne semble pas très bien fonctionner sous windows

    else:
      ## The parameters are registred here (once again it shouldn't happen here)
      # on enregistre les paramètres (encore une fois ça ne devrait normalement pas se faire ici)
      import valid_forms
      valid_forms.Valideur(None, None, None, self.fields).write_conf()

      print self.page.flush()
      try:
        synchronize.synchronize(self.db, self.fields.has_key("confirmation"))
        body_content=self.page.add_complex_option_tag("div",[("class","body_class")])
        body=body_content.add_complex_tag("fieldset")
        body.add_simple_tag("legend",_("Réussite de la synchronisation"))
        p=body.add_complex_tag("p")
        p.add_text(_("La synchronisation a été effectuée avec succès, votre site est à jour."))
      except synchronize.SyncError, error:
        body_content=self.page.add_complex_option_tag("div",[("class","body_class")])
        body=body_content.add_complex_tag("fieldset")
        body.add_simple_tag("legend",_("Échec de la synchronisation"))
        p=body.add_complex_tag("p")
        p.add_text(_("La synchronisation a échoué : « %s »." % error.get_error()))
        if error.is_conflict() and not self.fields.has_key("confirmation"):
          p.add_text(_("Des fichiers plus récents se trouvent sur le serveur, la synchronisation va les mettre à la place des fichiers locaux qui ont été modifiés. Êtes-vous sûr de vouloir effectuer la synchronisation ?"))
          body.add_br()
          body.add_br()
          form = body.add_form("admin.py?id=synchronize", "post")
          form.add_input("hidden","confirmation", '1')
          
          form.add_input("submit", "submit", _("Oui"))
          form = body.add_form("admin.py", "post")
          
          form.add_input("submit", "submit", _("Non"))
        else:
          p.add_text(_("Peut être que les paramètres de configuration sont erronés."))

    self.gen_nav()


  ## Generation of form number i
  #generation du formulaire numero i
  def generate(self):
    ids = {"main"       : self.gen_form_main,\
           "install"    : self.gen_form_install,\
           "general"    : self.gen_form_general,\
#           "pass"       : self.gen_form_pass,\
           "pages"      : self.gen_form_pages,\
           "delpage"    : self.gen_form_delpage,\
           "modpage"    : self.gen_form_modpage,\
           "editpage"   : self.gen_form_editpage,\
           "synchronize": self.gen_form_synchronize}
    try:
      ids[self.params["id"]]()
    except KeyError:
      try:
        module=self.params["id"]
      except:
        ids["main"]()
        print self.page.generate()
        return;
      modules=self.mm.get_available_modules()
      if module in modules:
        if isinstance(self.mm[module], module_interfaces.IModuleAdminPage):
          self.mm[module].generate_admin_xhtml(self)
      else:  
        ids["main"]()
    print self.page.generate()
