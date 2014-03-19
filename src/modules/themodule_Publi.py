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
##  - Finish the string parser in Bibtex_entry
##  - Finish lists manager (in particular edition)
##  - Offer differeny export ways (file to download...)
##  - Manage the *@STRINGS*
##  - General clean up
##  - Manage the comments
##  - Add messages after operations
##  - Manage google import better...
# TODO:
#   - finir le parser de string dans Bibtex_entry
#   - finir la gestion des listes (édition notamment)
#   - proposer différentes formes d'export (fichier à télécharger, etc)
#   - gérer les *@STRINGS*
#   - faire un nettoyage de printemps
#   - gérer les commentaires
#   - Ajouter des messages après opérations
#   - Gérer l'import google mieux...


from module_interfaces import *


from conf import confstatic
import conf_general, conf_private
from interface import class_forms
from db import db_manager
import urllib2, cookielib, re
import os

## Class that represent a BibTex entry
# Classe representant une entree BiBTeX 
class Bibtex_entry:
  ## Initializing some stuff: text to parse is input...
  # on initialise des p'tits trucs : on prend en entree le texte a parser...
  def __init__(self, text):
    self.type = ''
    self.args = []
    self.text = text.replace('\n','').lstrip()
    self.author     = ''
    self.title      = ''
    self.journal    = ''
    self.pages      = ''
    self.year       = ''
    self.publisher  = ''
    self.abstract   = ''
    self.note       = ''
    self.url        = ''
    self.parse()


  def __str__(self):
    return ("""Type : %s\n""" %(self.type))  + ("""Auteur: %s\n""" %(self.author))  + ("""Titre: %s\n""" %self.title)  + ("""Journal: %s\n""" %self.journal) + ("""Pages: %s\n""" %self.pages)\
      + ("""Annee: %s\n""" %self.year) + ("""Publie chez: %s\n""" %self.publisher) + ("""Abstract: %s\n""" %self.abstract)

  ## Parse what is on the right  of a " foo = 'bar' " equality
  # Parse ce qui est a droite d'une egalite de type truc = "machin"
  def parse_acc(self, text):
    i = 0
    while i < len(text) and text[i] != ',' and text[i] != '}':     
      if text[i] == '"':
        acc = 1
        try:
          while acc != 0 : 
            i = i + 1
            if text[i] == '"':
              acc = acc - 1
        except:
          print ""
      elif text[i] == '{':
        acc = 1
        try:
          while acc != 0 and i < len(text) - 1:
            i = i + 1          
            if text[i] == '}':
              acc = acc - 1
            if text[i] == '{':
              acc = acc + 1
        except:
          print "" 
      i = i + 1
    return (text[i+1:],text[0:i])
  
  ## Parsing a lign from a BibTex entry
  # on parse une ligne d'une entree BiBTeX
  def parse_line(self, text):
    t = text.lstrip()
    i = 0
    while i < len(t) - 1 and t[i] != ',' and t[i] != '}' and t[i] != '=':
      i = i + 1
    str1 = t[0:i]
    if t[i] == ',' or t[i] == '}':
      return (t[i+1:].lstrip().rstrip(), self.parse_string(str1.lstrip().rstrip()))
    str2 = t[t.find('=') +1:len(t)]
    str2 = str2.lstrip()
    res = self.parse_acc(str2)
    return (res[0].lstrip().rstrip(), str1.lstrip().rstrip(), self.parse_string(res[1].lstrip().rstrip()))

  ## Parsing the BibTex entry
  # Parse l'entree BiBTeX
  def parse(self):
    tmp  = re.match('@([^{]*){(.*)', self.text)
    try:  
      next = tmp.group(2)
      self.type = tmp.group(1)
    except:
      self.type = ''
      print self.text
      return

    while next != '':
      res = self.parse_line(next)
      next = res[0]
      if (len(res) < 3):
        self.args.append(res[1])
      else:
        if (res[1].lower() == 'author'):
          self.author = self.parse_string(res[2])
        elif (res[1].lower() == 'title'):
          self.title = self.parse_string(res[2])
        elif (res[1].lower() == 'journal'):
          self.journal = self.parse_string(res[2])
        elif (res[1].lower() == 'pages'):
          self.pages = self.parse_string(res[2])
        elif (res[1].lower() == 'year'):
          self.year = self.parse_string(res[2])
        elif (res[1].lower() == 'url'):
          self.pages = self.parse_string(res[2])
        elif (res[1].lower() == 'note'):
          self.year = self.parse_string(res[2])
        elif (res[1].lower() == 'publisher'):
          self.publisher = self.parse_string(res[2])
        elif (res[1].lower() == 'abstract'):
          self.abstract = self.parse_string(res[2])
        self.args.append((res[1],res[2]))

  ## Interprete BibTex strings:
  ## { blabla } becomes blabla
  ## todo: { foo } + { bar } # { whatever } ...
  # Interprete les chaines de caracteres BiBTeX:
  #   { blabla } est transforme en blabla
  #   a faire: { truc } + { truc } # {dernier_truc }, etc.
  def parse_string_unit (self,str):
    ch = ""
    if str[0] == '"' or str[0] == '{':
      ch = str[1:]
    if ch[-1] == '}' or str[-1] == '"':
      ch = ch[:-1]

    ## state is 1 if current state is under a '\', else state is 0
    ## acco is 1 if current state is inside {}, 0 else
    # state vaut 1 si on est sous le joug d'un \', 0 sinon
    # acco  vaut 1 si on est dans un {} 0 sinon
    state  = 0
    acco   = 0
    i      = 0
    ch_ret = ""
    ## accent is 0 if there is no accent
    ## accent is 1 if it is a '
    ## accent is 2 if it is a `
    ## accent is 3 if it is a ^
    ## accent is 4 if it is a "
    # accent vaut 0 si il n'y a pas d'accent
    #        vaut 1 si c'est un '
    #        vaut 2 si c'est un `
    #        vaut 3 si c'est un ^ 
    #        vaut 4 si c'est un "       
    accent = 0

    accent_dico = { 'a' : ['a', 'à', 'â', 'ä'],\
                    'e' : ['é', 'è', 'ê', 'ë'],\
                    'i' : ['i', 'i', 'î', 'ï'],\
                    'o' : ['o', 'o', 'ô', 'ö'],\
                    'u' : ['u', 'ù', 'û', 'ü'],\
                    'y' : ['y', 'y', 'y', 'ÿ']}
    ## Parsing the \' and \'{} ...
    # On parse les \' \'{} etc.
    while state != -1:
      ## If there is nothing special
      # Si on est dans rien de spécial
      if state == 0:
        if ch[i] == '{':
          acco += 1
        elif ch[i] == '}':
          acco -= 1
        elif ch[i] == '\\':
          i = i + 1
          if ch[i] == '\'':
            accent = 0
            state = 1 
          elif ch[i] == '`':
            accent = 1
            state = 1
          elif ch[i] == '^':
            accent = 2
            state = 1
          elif ch[i] == '"':
            accent = 3
            state = 1
          ## else
          # Sinon
          elif ch[i] == '\\':
            ch_ret += '\\' 
            state = 0 
          else:
            pass
        else:
          ch_ret += ch[i]

      ## If current state is under a simple {
      # Si on est sous un { simple
      elif state == 1:
        if ch[i] == '{':
          acco += 1
        ## Else accents
        # Sinon accents
        else:
          try:
            ch_ret += accent_dico[ch[i]][accent]
          except:
            ch_ret += ch[i]
          state = 0        

      i = i + 1
      if i == len(ch):
        state = -1

    return ch_ret.lstrip().rstrip()

  def parse_string(self, cmd):
    ch = ""
    try:
      ch = self.parse_string_unit(cmd)
      return ch
    except:
      return cmd

## Class corresponding to a BibTex document
# Classe correspondant a un document BiBTeX 
class Bibtex_doc:

  ## initialisation
  def __init__(self, text):
    self.num = 0
    self.entries = []
    self.parse_entries(text)

  ## Parsing all the entries of the document
  # On parse toutes les entrees du document
  def parse_entries(self, text):
    i,j = 0,0
    t = text
    l = len(t)
    while (i < l):
      i = t.find('@')
      j = t[i+1:].find('@')
      
      self.num = self.num + 1
      ## If there is still another entry
      # si on a encore une prochaine entree      
      if (j != -1):
        entry = Bibtex_entry(t[i:j+1])
        self.entries.append(entry)
        i,t = j+1,t[j+1:]
      else:
        entry = Bibtex_entry(t[i:])
        self.entries.append(entry)
        i = l

###
#
#  THE MODULE
#  LE MODULE
#
###

class TheModule(ComfortModule, IModuleContentProvider, IModuleDB, IModuleAdminPage):
  mode        = "both"

  def module_init(self):
    self.table_name  = "publi_items" 
    self.table_prefix = "publi"
    self.title_size  = 20
    self.author_size = 25
    self.journal_size = 25
    pass


  def module_admin_info(self):
    return "Permet de gérer vos publications."
  
  def module_title(self):
    return ""

  def module_name(self):
    return _("Publications")

  def module_id(self):
    return "Publi"

  def init_content(self):
    pass

  def handle_admin_request(self, params, fields):
    try:
      form = params["form"]
    except:
      form=""

    ## Adding a publishing to the database
    # Ajout d'une publication dans la BDD
    if form == "add_item":
      if fields.has_key("item_text"):
        self.parse_doc(fields["item_text"].value)
        return "admin.py?id=Publi"
      else:
        return "handler.py"

    ## Adding a .bib file
    # Ajout d'un fichier .bib
    elif form == "add_item_file":
      if fields.has_key("item_path"):
        fileitem = fields["item_path"]
        if fileitem.file:    
          try:
            buff = fileitem.file.read().decode('iso-8859-15')
          except:
            buff = fileitem.file.read()
          
          self.parse_doc(buff.encode('utf-8'))
          return "admin.py?id=Publi"
          
        else:
          return "handler.py"
      else:
        return "handler.py"


    ## Adding a document to a course
    # Ajout d'un document à un enseignement
    elif form == "add_pdf":
      if fields.has_key("item_path"):
        fileitem = fields["item_path"]
        if fileitem.file:
          try:      
            if fields.has_key("item_id"):
              name_f = "pub_"+ fields["item_id"].value + "_" + (fileitem.filename)    
              print os.path.join(confstatic.docs_path, name_f)
              fout = file (os.path.join(confstatic.docs_path, name_f), 'wb')
          except:
            return "admin.py?id=Publi1"
     
          fout.write (fileitem.file.read())
          fout.close()

          record = {'pdf'  : "pub_"+fields["item_id"].value+"_"+(fileitem.filename) }

          table_db = self.db.table(self.table_prefix+"_items")
          table_db.update(record, [("id","=",fields["item_id"].value)])
          return "admin.py?id=Publi"
        else:
          return ""
      else:
        return "handler.py" 


    ## Adding a publishing in the database
    # Ajout d'une publication dans la BDD
    elif form == "add_item2":
      if fields.has_key("item_title"):
        record = {  'title'    : fields['item_title'].value,\
                    'author'   : fields['item_author'].value,\
                    'journal'  : fields['item_journal'].value,\
                    'type'     : fields['item_type'].value.lower(),\
                    'publisher': "",\
                    'abstract' : fields['item_abstract'].value, \
                    'pages'    : "", \
                    'pdf'      : "", \
                    'year'     : fields['item_year'].value}
        table_db = self.db.table(self.table_prefix+"_items")
        table_db.insert(record)
        if fields["submit"].value==_("Terminé"):
          return "admin.py?id=Publi"
        else:
          return "admin.py?id=Publi&amp;form=add_item2"
      else:
        return "handler.py"

    ## Retrieving the publishings over Google Scholar
    # Récupération des publications sur Google Scholar
    elif form == "add_item3":
      if fields.has_key("item_name"):


        return "admin.py?id=Publi&amp;form=add_item3" ##Add an option in url ?
                                                      #rajouter une option dans l'url ?
      else:
        return "handler.py"


    ## Deletion of a publishing in the database
    # Suppression d'une publication dans la BDD 
    elif form == "del_item":
      if fields.has_key("item_id"):
        self.erase_publi(fields['item_id'].value)
        return "admin.py?id=Publi"
      else:
        return "handler.py"

    elif form == "edit_item":
      if fields.has_key("item_id"):   
        record = {'author'  : fields['item_author'].value, 'title'   : fields['item_title'].value, 'journal' : fields['item_journal'].value, 'year'    : fields['item_year'].value}

        table_db = self.db.table(self.table_prefix+"_items")
        table_db.update(record, [("id","=",fields["item_id"].value)])
        return "admin.py?id=Publi"
      else:
        return "handler.py"

    ## Validation of the adding of a list
    # Validation de l'ajout d'une liste
    elif form == "add_list":
      if fields.has_key("list_title"):   
        record = {'title'   : fields['list_title'].value, 'pub_list' : fields['list_pub'].value}

        table_db = self.db.table(self.table_prefix+"_lists")
        table_db.insert(record)
        return "admin.py?id=Publi&amp;form=list_main"
      else:
        return "handler.py"

    ## Deletion of a list
    # Suppression d'une liste  
    elif form == "del_list":
      if fields.has_key("list_id"):
        table = self.db.table(self.table_prefix+"_lists")
        table.delete([("id", "=", fields["list_id"].value)])
        return "admin.py?id=Publi&amp;form=list_main"
      else:
        return "handler.py"

    ## Emptying all the publis of a list
    # Vidons toutes les publi d'une liste
    elif form == "erase_all":
      if fields.has_key("id_list"):
        if fields['id_list'].value == "-1":
          table_db = self.db.table(self.table_prefix+"_items")
          table_db.delete([])
          table_db = self.db.table(self.table_prefix+"_lists")
          table_db.delete([])
        else:           
          publis = self.give_publications_from_list(fields['id_list'].value)
          for p in publis:
            self.erase_publi(str(p['id']))
        return "admin.py?id=Publi"
      else:
        return "handler.py"

    return "handler.py"
  

  ## Form to aministrate the publications
  # Le formulaire d'administration des publications 
  def generate_admin_xhtml(self, form_page):
    ## main is 0 if it is the basic page, 1 if one add a publishing, 2 else
    # main vaut 0 si c'est la page de base, 1 si on ajoute une publi, 2 sinon
    main = 0
    ## options list
    # Liste des options                       
    try:
      if form_page.params["form"] == "edit_item":
        main = 2
      elif form_page.params["form"] == "add_item":
        main = 1
      elif form_page.params["form"] == "add_item2":
        main = 1
      elif form_page.params["form"] == "add_item3":
        main = 1	
      elif form_page.params["form"] == "add_item3_confirm":
        main = 1	
      elif form_page.params["form"] == "list_main":
        main = 1
      elif form_page.params["form"] == "add_list":
        main = 1
      elif form_page.params["form"] == "add_pdf":
        main = 1
      elif form_page.params["form"] == "export_list":
        main = 1
      elif form_page.params["form"] == "erase_all":
        main = 1
    except:
      pass

    title=_("Gestion des publications")
    form_page.page = class_forms.Page(title,conf_general.style)
    title_content  = form_page.page.add_complex_option_tag("div",[("id","title")])
    title_content.add_text(title)

    form_page.gen_nav()

    ## Everything that is module operation precsely:
    ## - BibTex import
    ## - Form import
    ## - Publishings list management
    ## - Exportation of the publishings under BibTex format
    # Tout ce qui est opérations du module proprement dit: 
    # - importation BiBTeX
    # - importation par formulaire
    # - gestion des listes de publication
    # - exportation de publications au format BiBTeX
    body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
    body = body_content.add_complex_tag("fieldset")
    body.add_simple_tag("legend",_("Opérations sur les publications"))


    table_f = body.add_table(0,0,5)
    ## Button for the management of publishings
    # Bouton de gestion des Publications
    form_main = (class_forms.Content("", "")).add_form( "admin.py?id=Publi","post")
    form_main.add_input("submit", "submit", _("Gestion générale")) 
    ## BibTex import button
    # Bouton d'import BiBTeX
    form_import = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=add_item","post")
    form_import.add_input("submit", "submit", _("Importer une/des publication(s) sauce BiBTeX")) 
    ## Form import button
    # Bouton Importation Formulaire
    form_import2 = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=add_item2","post")
    form_import2.add_input("submit", "submit", _("Ajouter une publication par formulaire"))
    ## Button to import form through Google Scholar
    # Bouton Importation Formulaire via Google Scholar
    form_import3 = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=add_item3","post")
    form_import3.add_input("submit", "submit", _("GoogleImport")) 
    ## Button to manage the publishing lists
    # Bouton de gestion des listes de publication
    form_lists = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=list_main","post")
    form_lists.add_input("submit", "submit", _("Gérer les listes de publication")) 
    ## Button to add a publishing list
    # Bouton d'ajout d'une liste de publication
    form_list_add = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=add_list","post")
    form_list_add.add_input("submit", "submit", _("Ajouter une liste")) 

    table_f.add_line([("td", [], form_main), ("td", [], form_import), ("td", [], form_import2), ("td", [], form_import3), ("td", [], form_lists), ("td", [], form_list_add)])

    p = form_page.page.add_complex_tag("p")
    p.add_br()


    # ___________________________________________________________________ #
    #                                                                     #
    #                        Main form                                   ##
    #                    Formulaire principal          : XHTML 1.0 strict #
    # ___________________________________________________________________ #
    if main == 0:

      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")

      id_list = "-1"
      if form_page.params.has_key('id_list'):
        id_list = form_page.params['id_list']
        if id_list == "-1":
          body.add_simple_tag("legend",_("Publications enregistrées"))
        else:
          table_db = self.db.table(self.table_prefix+"_lists")
          list_db = table_db.select(cond = [("id", "=", "0")], order = [("id",True)])
          if len(list_db) == 0:
            id_list = "-1"
            body.add_simple_tag("legend",_("Publications enregistrées"))
          else:
            l = list_db.next()
            body.add_simple_tag("legend", l['title'])
      else:     
        body.add_simple_tag("legend",_("Publications enregistrées"))
      
  
      ## Retrieving the publishings list
      # Récupérons la liste des publications 
      if id_list != "-1":
        publis = self.give_publications_from_list(id_list)
        publis.sort(cmp = lambda x,y: cmp(x['title'], y['title']))
      else:
        table = self.db.table(self.table_prefix+"_items")
        publis = table.select(cond=[],order=[("id",True)])
        publis = [pub for pub in publis]


      ## Sorting it
      # Maintenant trions là
      if form_page.params.has_key('sort'):
        if form_page.params['sort'] == 'title' or \
           form_page.params['sort'] == 'year' or \
           form_page.params['sort'] == 'author' or \
           form_page.params['sort'] == 'type':

          if form_page.params.has_key('order'):
            if form_page.params['order'] == 'desc':
              publis.sort(cmp = lambda x,y: cmp(x[form_page.params['sort']],y[form_page.params['sort']]))
            elif form_page.params['order'] == 'asc':
              publis.sort(cmp = lambda y,x: cmp(x[form_page.params['sort']],y[form_page.params['sort']]))
               

      if len(publis) == 0:
        body.add_simple_tag("h3", _("Il n'y a aucune publication"))
      else: 
        if len(publis) == 1:
          body.add_simple_tag("h3", _("Il y a ")+str(len(publis))+ _(" publication dans la base de données"))
        else:
          body.add_simple_tag("h3", _("Il y a ")+str(len(publis))+ _(" publications dans la base de données"))
        body.add_link("admin.py?id=Publi&amp;form=erase_all&amp;id_list="+id_list, "Effacer toutes les publications listées")
        body.add_complex_tag("p")

        order = 'asc'
        if form_page.params.has_key('order'):
          if form_page.params['order'] == 'asc':
            order = 'desc'

        title_link = class_forms.Content("", "")
        title_link.add_link("admin.py?id=Publi&amp;sort=title&amp;order="+order+"&amp;id_list="+id_list, _("Titre de la publication"))
        author_link = class_forms.Content("", "")
        author_link.add_link("admin.py?id=Publi&amp;sort=author&amp;order="+order+"&amp;id_list="+id_list, _("Auteur(s)"))
        journal_link = class_forms.Content("", "")
        journal_link.add_link("admin.py?id=Publi&amp;sort=journal&amp;order="+order+"&amp;id_list="+id_list, _("Journal"))
        year_link = class_forms.Content("", "")
        year_link.add_link("admin.py?id=Publi&amp;sort=year&amp;order="+order+"&amp;id_list="+id_list, _("Année"))
        type_link = class_forms.Content("", "")
        type_link.add_link("admin.py?id=Publi&amp;sort=type&amp;order="+order+"&amp;id_list="+id_list, _("Type"))

        table_f = body.add_table(1,2,3)
        table_f.add_line([("th",[("align","center")], title_link), \
                          ("th",[("align","center")], type_link), \
                          ("th",[("align","center")], author_link), \
                          ("th",[("align","center")], journal_link), \
                          ("th",[("align","center")], class_forms.Text(_("Pages"))), \
                          ("th",[("align","center")], year_link), ("th",[("align","center")],\
                               class_forms.Text(_("Publié chez"))), ("th",[("align","center")], class_forms.Text(_("Actions"))) ])

        for publi in publis:
          ## The nice buttons on the right
          # Les p'tits boutons mignons de la droite
          commands = (class_forms.Content("", "")).add_table(0, 0, 2)

          form_add = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=add_pdf&amp;item_id="+str(publi["id"])+"","post")
          form_add.add_input("submit", "submit", _("Ajouter PDF")) 

          form_del = (class_forms.Content("", "")).add_form( "adminvalid.py?id=Publi&amp;form=del_item","post")
          form_del.add_input("hidden", "item_id", str(publi["id"]))
          form_del.add_input("submit", "submit", _("Supprimer")) 

          form_edit = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=edit_item&amp;item_id="+str(publi["id"])+"","post")
          form_edit.add_input("submit", "submit", _("Éditer")) 

          commands.add_line([("td", [], form_add), ("td", [], form_del), ("td", [], form_edit)])

          
          ## Fields are cut if too long
          # On coupe les champs si ils sont trop longs
          if len(publi['title']) < self.title_size:
            title = class_forms.Text(publi['title'])
          else:
            title = class_forms.Text(publi['title'][0:self.title_size] + '...')

          if len(publi['author']) < self.author_size:
            author = class_forms.Text(publi['author'])
          else:
            author = class_forms.Text(publi['author'][0:self.author_size] + '...')

          if len(publi['journal']) < self.journal_size:
            journal = class_forms.Text(publi['journal'])
          else:
            journal = class_forms.Text(publi['journal'][0:self.journal_size] + '...')

          table_f.add_line([ ("td",[("align","left")], title), \
                             ("td",[("align","left")], class_forms.Text(publi['type'])), \
                             ("td",[("align","left")], author), ("td",[("align","left")], journal), \
                             ("td",[("align","left")], class_forms.Text(publi['pages'])),\
                             ("td",[("align","left")], class_forms.Text(publi['year'])), \
                             ("td",[("align","left")], class_forms.Text(publi['publisher'])), \
                             ("td",[("align","right")], commands) ])

      body2 = body.add_complex_tag("p");
      body2.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                 Bibtex import form                                ##
    #             Formulaire d'importation BiBTeX      : XHTML 1.0 strict #
    # ___________________________________________________________________ #
    elif form_page.params["form"] == "add_item":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Importation de publications"))
      
      body.add_complex_tag("p")
      ## File to upload
      # Le fichier à uploader     
      form = body.add_complex_option_tag("form", [("action", "adminvalid.py?id=Publi&amp;form=add_item_file"),\
                                                  ("method", "post"), \
                                                  ("enctype","multipart/form-data")]) 
      p = form.add_complex_tag("p")  
      p.add_text("<b>Un fichier à importer (.bib): </b>")
      p.add_single_tag("input", [("type", "file"), ("name", "item_path"), ("accept", "*/*")])
      p.add_br()
      p.add_br()
      p.add_input("submit", "submit", _("Importer"))

      p.add_text("<hr/>")

      ## Text import
      # Importation texte
      form = body.add_form("adminvalid.py?id=Publi&amp;form=add_item", "post")
      p = form.add_complex_tag("p")  
      p.add_textarea_labeled(_("Ou bien du code BiBTeX à importer"), "item_text",10,100)
      p.add_br()
      p.add_br()
      p.add_input("submit", "submit", _("Importer"))

      
      p = form.add_complex_tag("p")   

    # ___________________________________________________________________ #
    #                                                                     #
    ##                       Adding form                                 ##
    #                     Formulaire d'ajout           : XHTML 1.0 strict #
    # ___________________________________________________________________ #
    elif form_page.params["form"] == "add_item2":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Ajout d'une publication"))

      ## Adding form
      # Le formulaire d'ajout
      form = body.add_form("adminvalid.py?id=Publi&amp;form=add_item2", "post")
      p = form.add_complex_tag("p")


      truc = class_forms.Content("","")
      truc.add_textarea("item_abstract",10,50)

      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_title", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Type")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_type", "article")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Auteur(s)")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_author", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Journal")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_journal", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Année")+" : ")), \
                        ("td",[("align","left")], class_forms.Input("text", "item_year", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Résumé")+" : ")), \
                        ("td",[("align","left")], truc) ])
      p.add_br()
      p.add_input("submit", "submit", _("Terminé"))
      p.add_input("submit", "submit", _("Ajouter une autre publication"))
      p.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                       Adding form                                 ##
    #                     Formulaire d'ajout           : XHTML 1.0 strict #
    # ___________________________________________________________________ #
    elif form_page.params["form"] == "add_item3":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Importation des publications via Google Scholar"))

      ## Adding form
      # Le formulaire d'ajout
      form = body.add_form("admin.py?id=Publi&amp;form=add_item3_confirm", "get")
      p = form.add_complex_tag("p")
      p.add_input("hidden", "id", "Publi")
      p.add_input("hidden", "form", "add_item3_confirm")
      p.add_input_maxlength("text", "item_name", "Critère de recherche sur Google Scholar", "100")
      p.add_br()
      p.add_input("submit", "submit", _("Rechercher"))
      p.add_br()

    elif form_page.params["form"] == "add_item3_confirm":
      google_cookie = cookielib.LWPCookieJar()
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(google_cookie))
      urllib2.install_opener(opener)
      ua = {'User-Agent': 'CoMFoRT'}
      url = 'http://scholar.google.fr/scholar_setprefs?q='+form_page.params['item_name']+'&lang=all&instq=&num=10&scis=yes&scisf=4&submit=E'
      request =urllib2.Request(url, None, ua)
      googlefile = urllib2.urlopen(request)
      ch_t = ""
      bib_list = re.findall('<a class=fl href="/scholar.bib(.*?)>.*?</a>',googlefile.read())
      for bib in bib_list:
        request = urllib2.Request('http://scholar.google.fr/scholar.bib'+bib, None, ua)
        ch_t += urllib2.urlopen(request).read() + "\n"
      self.parse_doc(ch_t)


    # ___________________________________________________________________ #
    #                                                                     #
    ##           Form for the adding the PDF file of a publi             ##
    #            Formulaire d'ajout de PDF d'une publi - XHTML 1.0 strict #
    # ___________________________________________________________________ #
    elif form_page.params["form"] == "add_pdf":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Ajout du PDF relatif à une publication"))
      
      body.add_complex_tag("p")    
      ## File to upload
      # Le fichier à uploader     
      form = body.add_complex_option_tag("form", [("action", "adminvalid.py?id=Publi&amp;form=add_pdf"),\
                                                  ("method", "post"), \
                                                  ("enctype","multipart/form-data")]) 
      p = form.add_complex_tag("p")  
      p.add_input("hidden","item_id",form_page.params["item_id"])
      p.add_text("<b>Le PDF à ajouter: </b>")
      p.add_single_tag("input", [("type", "file"), ("name", "item_path"), ("accept", "*/*")])
      p.add_br()
      p.add_br()
      p.add_input("submit", "submit", _("Importer"))
      
      p = form.add_complex_tag("p")   

    # ___________________________________________________________________ #
    #                                                                     #
    ##                       Edition form                                ##
    #                     Formulaire d'édition         : XHTML 1.0 strict #
    # ___________________________________________________________________ #
    elif main == 2:
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Édition d'une publication"))

      ## Retrieving all the information available on the publishing to edit
      # Recuperons toutes les infos disponibles pour la publication a editer
      table = self.db.table(self.table_prefix+"_items")
      publication = table.select(cond=[("id","=",form_page.params["item_id"])], order=[("id",True)]).next()

      form = body.add_form("adminvalid.py?id=Publi&amp;form=edit_item", "post")
      p = form.add_complex_tag("p")
      p.add_input("hidden","item_id",form_page.params["item_id"])

      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_title", publication["title"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Auteur(s)")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_author", publication["author"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Journal")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_journal", publication["journal"])) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Année")+" : ")), ("td",[("align","left")], class_forms.Input("text", "item_year", publication["year"])) ])
      p.add_br()
      p.add_input("submit", "submit", _("Éditer la publication"))

    # ___________________________________________________________________ #
    #                                                                     #
    ##                        List management form                       ##
    #                    Formulaire de gestion des listes                 #
    # ___________________________________________________________________ #
    elif form_page.params["form"] == "list_main":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Listes de publications enregistrées"))
      
      ## Getting all the publishings
      # On recupere toutes les publications 
      table = self.db.table(self.table_prefix+"_lists")
      list_db = table.select(cond=[] , order = [("id",True)])
      if len(list_db) == 0:
        body.add_simple_tag("h3", _("Il n'y a aucune liste, on en crée une ?"))
      else: 
        if len(list_db) == 1:
          body.add_simple_tag("h3", _("Il y a ")+str(len(list_db))+ _(" liste dans la base de données"))
        else:
          body.add_simple_tag("h3", _("Il y a ")+str(len(list_db))+ _(" listes dans la base de données"))

        table_f = body.add_table(1,0,1)
        table_f.add_line([("th",[("align","center")], class_forms.Text(_("Nom de la liste"))), \
                          ("th",[("align","center")], class_forms.Text(_("Nombre de publications"))), \
                          ("th",[("align","center")], class_forms.Text(_("Actions"))) ])

        for list_i in list_db:
          ## The nice buttons on the right
          # Les p'tits boutons mignons de la droite
          commands = (class_forms.Content("", "")).add_table(0, 0, 2)
          form_del = (class_forms.Content("", "")).add_form( "adminvalid.py?id=Publi&amp;form=del_list","post")
          form_del.add_input("hidden", "list_id", str(list_i["id"]))
          form_del.add_input("submit", "submit", _("Supprimer")) 

          form_edit = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=edit_list&amp;list_id="+str(list_i["id"]),"post")
          form_edit.add_input("submit", "submit", _("Éditer"))

          form_export = (class_forms.Content("", "")).add_form( "admin.py?id=Publi&amp;form=export_list&amp;list_id="+str(list_i["id"]),"post")
          form_export.add_input("submit", "submit", _("Exporter (BiBTeX)")) 

          commands.add_line([("td", [], form_del), ("td", [], form_edit), ("td", [], form_export)])


          ## Fileds are cut if too long
          # On coupe les champs si ils sont trop longs
          if len(list_i['title']) < self.title_size:
            title = class_forms.Content("", "")
            title.add_link("admin.py?id=Publi&amp;id_list="+str(list_i["id"]), list_i['title'])
          else:
            title = class_forms.Content("", "")
            title.add_link("admin.py?id=Publi&amp;id_list=" +str(list_i["id"]), list_i['title'][0:self.title_size] + '...')

          table_f.add_line([ ("td",[("align","left")], title), ("td",[("align","left")], class_forms.Text(str(list_i['pub_list'].count("-") - 1))), ("td",[("align","right")], commands) ])

      body2 = body.add_complex_tag("p");
      body2.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                      Extracting a list to BibTex                  ##
    #                    Extraction d'une liste vers BibTex               #
    # ___________________________________________________________________ #
    elif form_page.params["form"] == "export_list":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend", 'Exportation vers BiBTeX')
      p = body.add_complex_tag("p")
      te = p.add_textarea_labeled(_("Code BiBTeX"), "item_text",30,130)

      table_db = self.db.table(self.table_prefix+"_lists")
      list_db = table_db.select(cond = [("id", "=", form_page.params["list_id"])], order = [("id",True)])
      l = list_db.next()
  
      next = l['pub_list']
      id_list = []
      tmp  = re.match('-([^-]*)(-.*)', next)
      next = tmp.group(2)
      id_list.append(tmp.group(1))
      te.add_text(self.export_publication(tmp.group(1)))
      while tmp.group(2) != '-':
        tmp  = re.match('-([^-]*)(-.*)', next)
        next = tmp.group(2)
        te.add_text(self.export_publication(tmp.group(1)))

    
      body2 = body.add_complex_tag("p")
      body2.add_br()

    # ___________________________________________________________________ #
    #                                                                     #
    ##                   Deletion of the publis of a whole list          ##
    #                    Effacement des publi de toute une liste          #
    # ___________________________________________________________________ #
    elif form_page.params["form"] == "erase_all":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend", 'Voulez-vous vraiment tout effacer dans cette liste ?')

      form = body.add_form("adminvalid.py?id=Publi&amp;form=erase_all", "post")
      p = form.add_complex_tag("p")
      p.add_input("hidden","id_list",form_page.params["id_list"])
      
      p.add_input("submit", "submit", _("Oui, on efface tout !"))


    # ___________________________________________________________________ #
    #                                                                     #
    ##                       Adding form                                 ##
    #                     Formulaire d'ajout           : XHTML 1.0 strict #
    # ___________________________________________________________________ #
    elif form_page.params["form"] == "add_list":
      body_content = form_page.page.add_complex_option_tag("div",[("class","body_class")])
      body = body_content.add_complex_tag("fieldset")
      body.add_simple_tag("legend",_("Ajout d'une liste de publications"))

      ## Adding form
      ## - list_title is the name of the list
      ## - list_pub is the list of the publishings with the right format
      # Le formulaire d'ajout
      # - list_title contient le nom de la liste
      # - list_pub contient la liste des publications au bon format
      form = body.add_complex_option_tag("form",[ ("action" , "adminvalid.py?id=Publi&amp;form=add_list"),
          ("method" , "post"),
          ("id"     , "formulaire")])

      p = form.add_complex_tag("p")

      ## Javascript functions allow handful stuffs
      # Les fonctions javascript qui permettent de faire des trucs pratiques
      body.add_text( "<script language=\"javascript\" type=\"text/javascript\">\n 		function moveSelectedOptions(from, to){\n 			fromSelect = document.getElementsByName(from)[0];		\n 			selOpt = getSelectedOptions(fromSelect);			\n\
			var selValues = new Array();\n 			if(selOpt.length>0){				\n 				selValues = getSelectedValues(fromSelect);\n 				toSelect=document.getElementsByName(to)[0];\n 				for(i=0;i<selOpt.length;i++){\n 					option = selOpt[i];\n 					fromSelect.removeChild(option);						\n 					toSelect.appendChild(option);\n\
				}\n 			}	\n 			return selValues;\n 		}\n 		\n 		function getSelectedValues (select) {\n 			var selValues = new Array();\n 			for (j = 0; j < select.options.length; j++){\n\
				selValues[selValues.length] = select.options[j].value;					\n 			}\n 			return selValues;\n 		}\n 		\n 		function getSelectedOptions (select) {\n 			var selOptions  = new Array();\n 			for (m = 0; m < select.options.length; m++){\n\
				if (select.options[m].selected) {\n 					selOptions[selOptions.length] = select.options[m];\n 				}\n 			}\n 			return selOptions;\n 		}\n \n 		//Affichage des valeurs dans le champ caché\n\
		function displayOptionsList(list)\n {\n var msg=\"-\";\n if (list.length == 0)\n msg = \"--\";\n for(n = 0; n < list.length; n++)\n {\n option = list[n];\n\
        msg += \"\"+option.value+\"-\";\n }\n document.getElementById('formulaire').list_pub.value = msg;\n }</script>")      
      
      p.add_input("hidden", "list_pub", "--") 

      
      pubs_l = self.give_publications()
      num_pubs = len(pubs_l)
      select_opt = []
      for pub_i in pubs_l:
        select_opt.append(([("value", str(pub_i[0]))], pub_i[1]))

      select_f = (class_forms.Content("","")).add_complex_option_tag("select", [("name","exchange1"),("multiple","multiple"),("size","10"),("style", "width:300px;")])
      select_f2 = (class_forms.Content("","")).add_complex_option_tag("select", [("name","exchange2"),("multiple","multiple"),("size","10"),("style", "width:300px;")])
    
      for opt in select_opt:
        temp = select_f.add_complex_option_tag("option", opt[0])
        temp.add_text(opt[1])

      bouton1 = (class_forms.Content("",""))
      bouton1.add_single_tag("input",  [("type",  "button"), ("value", "ajouter"), ("onclick", "list = moveSelectedOptions('exchange1','exchange2'); displayOptionsList(exchange2);")])

      bouton2 = (class_forms.Content("",""))
      bouton2.add_single_tag("input",  [("type",  "button"), ("value", "enlever"), ("onclick", "list = moveSelectedOptions('exchange2','exchange1'); displayOptionsList(exchange2);")])

      bouton2.add_single_tag("input",  [("type",  "button"), ("value", "monter"), ("onclick", " moveSelectedOptions('exchange2','exchange1'); displayOptionsList(exchange2);")])

      bouton2.add_single_tag("input",  [("type",  "button"), ("value", "descendre"), ("onclick", " moveSelectedOptions('exchange2','exchange1'); displayOptionsList(exchange2);")])

      table_f = p.add_table(0,0,3)
      table_f.add_line([("td",[("align","left")], class_forms.Text(_("Titre")+" : ")), ("td",[("align","left")], class_forms.Input("text", "list_title", "")) ])
      table_f.add_line([("td",[("align","left")], class_forms.Text("")), ("td",[("align","left")], select_f), ("td",[("align","left")],\
                   select_f2), ])
      table_f.add_line([("td",[("align","left")], class_forms.Text("")), ("td",[("align","left")], bouton1), ("td",[("align","left")], bouton2)
                 ])
      p.add_br()
      p.add_input("submit", "submit", _("Ajouter la liste"))
      p.add_br()


    ## __ End of the page __
    # ___ Bas de la page ___
    form_page.gen_nav()


# ___________________________________________________________________________ 
#                                                                           
##                   Printing the XML content
#                    Affichage du contenu XML                       
# ___________________________________________________________________________
## It is ugly.
# c'est très moche.
  def generate_content_xml(self, args):
    ch = ""

    if args.has_key('list'):
      publis = self.give_publications_from_list(args['list'])
    else:
      publis = None

    if publis == None:
      ## Parsing data from database to DocBook
      #Parse les donnees de la BDD en DocBook.
      table = self.db.table(self.table_prefix+"_items")
      publis = table.select(cond=[],order=[("id",True)])

    ## List sorting
    # Tri de la liste
    if args.has_key('publi_sort'):
      if args['publi_sort'] == 'title'  or args['publi_sort'] == 'year'   or args['publi_sort'] == 'author' or args['publi_sort'] == 'type':
        if args.has_key('publi_order'):
          if args['publi_order'] == 'desc':
            publis.sort(lambda x,y: cmp(x[args['publi_sort']],y[args['publi_sort']]))
          elif args['publi_order'] == 'asc':
            publis.sort(lambda x,y: cmp(y[args['publi_sort']],x[args['publi_sort']]))
        else:          
          publis.sort(lambda x,y: cmp(x[args['publi_sort']],y[args['publi_sort']]))
             

    ## Function a bit useless, but it looks cleaner this way
    # fonction un peu inutile, mais ça fait plus propre comme ça
    def add_str(chaine, string):
      chaine += string +"\n"
      return chaine
   
    ch = add_str(ch, "<bibliography>")

    for item in publis:
      ch = add_str(ch, "<bibliomixed>")
      ch = add_str(ch, "<bibliomset relation='article'>") ## To rewrite, it is
                                                          ##needed to check if
                                                          ##it is an article or
                                                          ##a book for instance.
                                                          #A revoir, il faut
                                                          #savoir si c'est un
                                                          #livre ou un article
                                                          #par exemple

      if item['pdf'] == "":   
        ch += ("""<title><ulink url="#"><emphasis role=\"strong\">%s</emphasis></ulink></title>""")\
               %(self.pub_display(item['title']))
      else:
        ch += ("""<title><ulink url="%s"><emphasis role=\"strong\">%s</emphasis></ulink></title>""")\
                %(confstatic.get_docs_url(item['pdf']), self.pub_display(item['title']))

      if item.has_key('abbrev'):
        ch = add_str(ch, "<abbrev>" + item['abbrev'] + "</abbrev>")
      
      ## Author, if there is none, nothing is put
      ## Management of multiple authors
      # Auteur, si il n'y en a pas, on ne met rien ! 
      # Gestion des auteurs multiples ?
      if item.has_key('author'): 
        ch = add_str(ch, "<author>")
        ch = add_str(ch, "<personname>" + item['author'] + "</personname>")
        ch = add_str(ch, "</author>")

      ## Date
      if item.has_key('date'):
        ch = add_str(ch, "<pubdate>" + item['date'] + "</pubdate>")

      ## Abstract
      # Résumé
      if item.has_key('abstract'):
        ch = add_str(ch, "<abstract>" + self.pub_display(item['abstract']) + "</abstract>") 
      ch = add_str(ch, "</bibliomset>")

      if item.has_key('journal'):
        ch = add_str(ch, "<bibliomset relation='journal'>")
        ch = add_str(ch, "<title>" + item['journal'] + "</title>")
        if item.has_key('publisher'):
          ch = add_str(ch, "<publishername>" + self.pub_display(item['publisher']) + "</publishername>")
        ch = add_str(ch, "</bibliomset>")
      ch = add_str(ch, "</bibliomixed>")

    ch = add_str(ch, "</bibliography>")
    #ch = add_str(ch, "<ulink url=\"#\">Tri par titre</ulink><emphasis role=\'strong\'> - </emphasis>\n")
    #ch = add_str(ch, "<ulink url=\"#\">Tri par auteur</ulink><emphasis role=\'strong\'> - </emphasis>\n")
   # ch = add_str(ch, "<ulink url=\"#\">Tri par année</ulink><emphasis role=\'strong\'> - </emphasis>\n")
  #  ch = add_str(ch, "<ulink url=\"#\">Tri par type</ulink>\n")
    
    return ch

  def setup_db(self, db):
    self.db    = db
    ## Publishing table creation
    # Création de la table des publications
    schema = {'author'   : 'text', \
              'title'    : 'text', \
              'journal'  : 'text', \
              'type'     : 'varchar', \
              'abstract' : 'varchar', \
              'pages'    : 'varchar', \
              'publisher': 'text',\
              'pdf'      : 'varchar',\
              'year'     : 'text'}
    try:
      self.db.table(self.table_prefix+"_items")
    except:
      self.db.create(self.table_prefix+"_items", schema);

    ## Creation of the table for the publishings list
    # Création de la table des listes de publications
    schema = {'title':'text', 'pub_list':'text'}
    try:
      self.db.table(self.table_prefix+"_lists")
    except:
      self.db.create(self.table_prefix+"_lists", schema);

  ## Recording the publishing in the database
  # enregistre la publication dans la db
  def save_publication(self, pub):
    record = {'author':pub.author,\
              'title':pub.title, \
              'journal':pub.journal, \
              'type':pub.type.lower(), \
              'publisher':pub.publisher,\
              'abstract':pub.abstract, \
              'pages':pub.pages, \
              'pdf': "", \
              'year':pub.year}
    table = self.db.table(self.table_prefix+"_items")
    table.insert(record)
    
  ## Take out of the database the publishing(s) that satisfy the conditions list
  # enleve la/les publication(s) dans la db qui satisfait la liste de conditions
  def remove_publication(self, conditions):
    table = self.db.table(self.table_prefix+"_items")
    table.delete(conditions)        

  def parse_doc(self, text):
    parse = Bibtex_doc(text)
    for pub in parse.entries:
      self.save_publication(pub)

  def give_publications(self):
    res = []
    table_db   = self.db.table(self.table_prefix + "_items")
    items_db = table_db.select(cond = [], order = [("id", True)])
    for item_db in items_db:
      res.append((str(item_db['id']), item_db['title']))
    return res


  ## It is given the id of a list, it answers a publishing list!
  # On lui donne l'ID d'une liste de publi, et il renvoie une liste de publis ! 
  def give_publications_from_list (self, id_list):
    try:
      res = []
      table_db   = self.db.table(self.table_prefix + "_lists")
      lists_db = table_db.select(cond = [("id","=",id_list)], order = [("id", True)])
      list_db = lists_db.next()

      next = list_db['pub_list']
      tmp  = re.match('-([^-]*)(-.*)', next)
      next = tmp.group(2)
      table_db   = self.db.table(self.table_prefix + "_items")
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

  def give_publications_from_ids (self, list__it):
    res = []
    table_db   = self.db.table(self.table_prefix + "_items")
    for id_i in list__it:
      items_db = table_db.select(cond = [("id","=",id_i)], order = [("id", True)])
      for item_db in items_db:
        res.append(item_db['title'])
    return res

  def export_publication(self, id_pub):
    table_db   = self.db.table(self.table_prefix + "_items")
    items_db   = table_db.select(cond = [("id","=",id_pub)], order = [("id", True)])
    res        = "" 

    for publi in items_db:
      res += "@"+ publi['type'] + "{\n"
      if publi['title'] != "":
        res += "  title\t\t"+"= {"+publi['title']+"},\n"
      if publi['author'] != "":
        res += "  author\t"+"= {"+publi['author']+"},\n"
      if publi['journal'] != "":
        res += "  journal\t"+"= {"+publi['journal']+"},\n"
      if publi['publisher'] != "":
        res += "  publisher\t"+"= {"+publi['publisher']+"},\n"
      if publi['pages'] != "":
        res += "  pages\t\t"+"= {"+publi['pages']+"},\n"
      if publi['abstract'] != "":
        res += "  abstract\t"+"= {"+publi['abstract']+"},\n"
      if publi['year'] != "":
        res += "  year\t\t"+"= {"+publi['year']+"},\n"
      res += "}\n\n"
    return res
  
    
  def display_title (self, title):
    ch = ''
    for i in range(len(title)):
      if title[i] != '{' and title[i] != '}':
        ch = ch + title[i]
    return ch

  def pub_display(self, title):
    ch = ""
    ch = title
    ch = ch.replace('{', '')
    ch = ch.replace('}', '')
    ch = ch.replace("\\`a", "à")
    ch = ch.replace("\\'e", "é")
    ch = ch.replace("\\`e", "è")
    ch = ch.replace("\\^e", "ê")
    ch = ch.replace("\\&", "&")
    ch = ch.replace("\\", "")
    return ch

  def erase_publi(self, id_item):
    table_db = self.db.table(self.table_prefix+"_items")
    table_db.delete([("id", "=", id_item)])
    ## Scanning every list and take it off of the ones where it is
    # On va scanner toutes les listes et le virer de celles où elle est
    table_db = self.db.table(self.table_prefix + "_lists")
    lists_db = table_db.select(cond=[("pub_list", "LIKE", "%-"+id_item+"-%")],order=[("id",True)])
    for l in lists_db:
      if l['pub_list'].count('-') == 2:
        table_db.delete([("id", "=", l["id"])])
      else:
        record = {'pub_list' : l['pub_list'].replace("-"+id_item+"-", "-") }
        table_db.update(record, [("id","=",l['id'])])
        
