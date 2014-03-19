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
import conf_general

class Content:
  """
    Classe de base pour stocker le contenu XHTML
  """
  def __init__(self, begin_tag, end_tag): 
    """
      begin_tag: balise ouvrante commencant le code XHTML
      end_tag: balise fermante terminant le code XHTML
    """
    self.elements=[]
    self.begin_tag=begin_tag
    self.end_tag=end_tag



  def add_text(self, text):
    """
      Ajoute du texte
    """
    c=Content(text,"")
    self.elements.append(c)



  def add_single_tag(self, tag, options):
    """
      Ajoute une balise du type <balise /> contenant eventuellement des options
      options: doit être une liste de couple
    """
    opt_str=""
    for o in options:
      opt_str=opt_str+" "+o[0]+"=\""+o[1]+"\""
    c=Content("""<%s%s />""" %(tag,opt_str),"")
    self.elements.append(c)    
  


  def add_simple_tag(self, tag, text):
    """
      Ajoute le texte "text" a l'intérieur de la balise "tag"
    """
    c=Content("""<%s>""" %(tag), """</%s>""" %(tag))
    c.add_text(text)
    self.elements.append(c)



  def add_complex_tag(self, tag):
    """
      Rajoute une balise "tag" et renvoit son conteneur
    """
    c=Content("""<%s>""" %(tag), """</%s>""" %(tag))
    self.elements.append(c)
    return c



  def add_complex_option_tag(self, tag, options):
    """
      Rajoute une balise ouvrante et fermante de type "tag".
      La balise ouvrante contient des options.
      options: doit être une liste de couple
      Renvoit le conteneur de la balise
    """
    opt_str=""
    for o in options:
      opt_str=opt_str+" "+o[0]+"=\""+o[1]+"\""
    c=Content("""<%s%s>""" %(tag,opt_str),"""</%s>""" %(tag))
    self.elements.append(c)
    return c



  def add_br(self):
    """
      Ajoute une balise br
    """
    self.add_single_tag("br",[])



  def add_hr(self):
    """
      Ajoute une balise hr
    """
    self.add_single_tag("hr",[])



  def add_img(self, addr, alt):
    """
      Ajoute une image
    """
    self.add_single_tag("img",[("src",addr),("alt",alt)])



  def add_link(self, addr, text):
    """
      Ajoute un lien hyper-texte
      addr: adresse du lien
      text: texte du lien
    """
    c=self.add_complex_option_tag("a",[("href",addr)])
    c.add_text(text)



  def add_input_maxlength(self, input_type, name, text, size):
    """
      Ajoute une balise input de type "input_type", de nom "name" 
      , de valeur "value" et de taille max "size"
    """
    self.add_single_tag("input",[("type",input_type),("name",name), ("value",text), ("maxlength",str(size)),("size",str(size)) ])


  def add_input(self, input_type, name, text):
    """
      Ajoute une balise input de type "input_type", de nom "name" 
      et de valeur "value"
    """
    self.add_single_tag("input",[("type",input_type),("name",name), ("value",text)])


  def add_labeled_input(self, input_type, label, name, text):
    """
      Raccourci pour ajouter <p> label : <input type="... /></p>
    """
    p=self.add_complex_tag("p")
    p.add_text(label+" : ")
    p.add_input(input_type, name, text)



  def add_select(self, name, options, id=""):
    """
      Ajoute une balise "select" de nom "name" avec les options "options"
      options: doit être une liste de couple (param de la balise option,texte)
        param de la balise option: une liste de couples (parametre,valeur)
          paramètre: string
          valeur: string
        texte: string
    """
    select=self.add_complex_option_tag("select",[("name",name), ("id", id)])
    for o in options:
      opt=select.add_complex_option_tag("option",o[0])
      opt.add_text(o[1])



  def add_form(self, action, method, id=""):
    """
      Rajoute une balise form d'action "action" utilisant la méthode "method"
      et renvoit le conteneur de la forme et renvoit son conteneur
    """
    if id=="":
      return self.add_complex_option_tag("form",[("action",action), ("method",method)])
    else:
      return self.add_complex_option_tag("form",[("action",action), ("method",method), ("id", id)])


  def add_textarea(self, name, rows, cols):
    """
      Ajoute une balise textarea et renvoit son conteneur
    """
    c = self.add_complex_option_tag("textarea",[("name",name), ("rows",str(rows)), ("cols",str(cols))])    
    return c



  def add_textarea_labeled(self, label, name, rows, cols):
    """
      Ajoute une balise textarea avec label et renvoit son conteneur
    """
    l=self.add_complex_tag("b")
    l.add_text(label+" : ")
    l.add_br()
    c = self.add_complex_option_tag("textarea",[("name",name), ("rows",str(rows)), ("cols",str(cols))])    
    return c



  def add_table(self, border, cellspacing, cellpadding):
    """
      Ajoute un tableau et renvoit son conteneur
    """

    return self.add_complex_option_tag("table",[("border",str(border)), ("cellspacing",str(cellspacing)),("cellpadding",str(cellpadding))])



  def add_line(self,l):
    """
      Ajoute une ligne
      l: c'est une liste des cases de la ligne.
      Chaque case est un triplet (balise,option,conteneur)
      balise: "td" ou "th"
      option: une liste de couple (paramètre,valeur)
      conteneur: une classe Text,Br,Hr,Link,Image,Input
    """
    line=self.add_complex_tag("tr")
    for e in l:
      column=line.add_complex_option_tag(e[0],e[1])
      column.elements.append(e[2])



  def generate(self):
    """
      Génère le code XHTML
    """
    s = self.begin_tag
    simple=len(self.elements)>1
    if simple:
      s = s + "\n"
    for element in self.elements:        
      s = s + element.generate()
      if simple:
        s = s + "\n"
    s = s + self.end_tag
    return s


class Page(Content):
  """
    conteneur pour une page html: s'occupe de générer le header
  """
  def __init__(self, title, style):
    """
      title: titre de la page
    """
    self.flushed=[]
    self.title=title
    self.elements=[]
    self.begin_tag=""
    self.end_tag=""
    self.style=style

  def generate_header(self):
    """
      Genere le header du code XHTML
    """
    self.header_generated = True
    style_link="""<link rel="stylesheet" href="../styles/admin/%s" type="text/css"  media="screen"/>""" % conf_general.adminstyle
    return ("""
      <!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">
      <html xmlns=\"http://www.w3.org/1999/xhtml\"> \n <head> \n <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
      <title>%s</title> %s
      <link rel="shortcut icon" href="../styles/favicon.png" type="image/x-icon" />
      </head>
      <body>""" %(self.title, style_link))

  def generate(self):
    """
      Genere le code XHTML
    """
    s = self.flush()
    s = s + "</body>\n</html>\n"
    return s

  def flush(self):
    """
      Genere le code XHTML actuel
    """
    if self.flushed==[]:
      s = self.generate_header()
      self.flushed.append(s)
    else:
      s = ""
    for element in self.elements:
      se = element.generate()
      s = s + se + "\n"
      self.flushed.append(se)
      self.elements = self.elements[1:]
    return s


def Text(text):
  """
    Macro renvoyant un conteneur avec du texte
  """
  c=Content("","")
  c.add_text(text)
  return c


def Input(input_type, name, text):
  """
    Macro renvoyant un conteneur avec une balise input
  """ 
  c=Content("","")
  c.add_input(input_type, name, text)
  return c


def Input_maxlength(input_type, name, text, size):
  """
    Macro renvoyant un conteneur avec une balise input
  """ 
  c=Content("","")
  c.add_single_tag("input",[("type",input_type), ("name",name), ("value",text), ("maxlength",str(size))])
  return c


def Textarea(name, rows, cols):
  """
    Macro renvoyant un conteneur avec une balise textarea
  """ 
  c=Content("","")
  c.add_textarea(name, rows, cols)
  return c


def Select(name, options, id=""):
  """
    Macro renvoyant un conteneur avec une balise select
  """ 
  c=Content("","")
  c.add_select(name, options, id=id)
  return c


def Image(addr, alt):
  """
    Macro renvoyant un conteneur avec une balise img
  """
  c=Content("","")
  c.add_img(addr, alt)
  return c
  
