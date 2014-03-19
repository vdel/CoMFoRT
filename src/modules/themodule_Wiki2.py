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
try:
  import hashlib
except ImportError:
  import md5 as hashlib
from module_interfaces import *
from modules import module_manager



from conf import confstatic
import conf_general, conf_private
from conf import utils
from db import db_manager
from interface import class_forms


#########      Parser Wiki (wikipedia syntax)      #########
#########    Parser Wiki (syntaxe de wikipédia)    #########   
title_tags = ["h2", "h3", "h4", "h5","h6"]
list_tags = ["ul", "li", "ol"]
pos_tags = ["center"]
format_tags = ["s","highlight","u","b","i","pre","big","small","sub","sup","ref"]
dont_parse_tags = ["math","nowiki"]
all_tags = title_tags+list_tags+pos_tags+format_tags+dont_parse_tags
single_tags_para = ["br","module"]
single_tags_not_para = ["hr"]

class Token:
  """ Token wiki: description:
    La classe Token contient deux variables: ttype, arg
    Voici la liste des différents types de token:
    - * : arg = nbr de * à la suite (doit commencer une ligne)
    - # : arg = nbr de # à la suite (doit commencer une ligne)
    - = : arg = nbr de = à la suite (doit commencer une ligne)
    - : : arg = nbr de : à la suite (doit commencer une ligne)
    - ' : arg = nbr de ' à la suite
    - space : un espace en début de ligne, pas d'argument (doit commencer une ligne)
    - return : saut de ligne, pas d'argument
    - [ : un crochet ouvrant
    - [[ : un double-crochet ouvrant
    - ] : un crochet fermant
    - ]] : un double-crochet fermant
    - {{ : exposant ou indice
    - }} : fin exp ou ind
    - {| : début tableau
    - |+ : titre
    - |- : nouvelle ligne
    - !  : cellule grisée
    - |  : nouvelle colonne
    - |} : fin tableau
    - tag_open : une balise ouvrante
    - tag_close : une balise fermante
            Voiçi la liste des arg possibles:
            - h2, h3, h4, h5
            - ul, li, ol
            - center
            - s, u, b, i, highlight
            - big, small
            - sub, sup
            - math
            - nowiki, pre
            - ref
    - tag : un tag sans balise fermante   
            Voiçi la liste des arg possibles:
            - hr, br, references
    - text : arg = le texte
    - eof
  """        
  def __init__(self,ttype,arg,arg2=None):
    self.ttype=ttype 
    self.arg=arg
    self.arg2=arg2

class WikiTree:
  """
    Arbre d'interprétation pour le wiki
      - self.tag indique la balise docbook correspondante
      - self.node est la liste des arbres inclus entre la balise ouvrante
        et fermante si self.tag!="text", le texte sinon
      - self.args: une liste de couple (paramètre XHTML de la balise, valeur)
  """
  def __init__(self, tag, args=None, text=None, single=False, escape=True):
    self.tag=tag
    self.args=args
    self.escape=escape
    if self.tag=="text":
      self.node=text  ## A leaf of the tree #une feuille de l'arbre
    else:
      self.node=[]    ## A node of the tree #un noeud de l'arbre
    self.single=single

  def add(self,tree):
    if self.tag=="text":
      self.node+=tree
    else:
      self.node.append(tree)

  def escape_str(self,string):
    s=""
    for c in string:
      if   c=='\"': s+="\\\""
      elif c=='\'': s+="\\\'"
      else: s+=c
    return s
   

  def generate(self,escape=True,escapeLatex=False):
    escape=self.escape and escape
    if self.tag=="text":
      if escape:
        ## <,>," and & are transformed into HTML code
        #on transforme les <, >, " et & en code HTML
        s=""
        for c in self.node:
          if c=="\"":
            s+="&quot;"
          elif c=="&":
            s+="&amp;"
          elif c=="<":
            s+="&lt;"
          elif c==">":
            s+="&gt;"
          else:
            s+=c          
        return s
      elif escapeLatex:
        s=""
        last=""
        for c in self.node:
          if c=="\'":
            if last=="\\":
              s+=" "          
            s+="\\textquoteright "
          else:
            s+=c
          last=c         
        return s
      else:
        return self.node  
    else:
      if len(self.node)!=0 or (self.tag!="sect1" and self.tag!="sect2" and self.tag!="sect3" and self.tag!="sect4" and self.tag!="sect5"):
        s=""
        if self.tag!="":
          s+="<"
          s+=self.tag
          if self.args!=None:
            for a in self.args:
              s+=""" %s=\"%s\""""%(a[0],self.escape_str(a[1]))
          if self.single:
            s+=" />"
          else:
            s+=">"
        for t in self.node:
          s+=t.generate(escape=escape,escapeLatex=escapeLatex)
        if not self.single and self.tag!="":
          s+="""</%s>"""%(self.tag)
        return s
      else:
        return ""


class Reader:
  """
    Contient le texte wiki
  """
  def __init__(self,wiki):
    self.wiki=wiki
    self.i=0;
    self.max=len(wiki)
    self.deb_ligne=True
  
  def current_char(self):
    if self.i>=self.max:
      return "eof"
    else:
      return self.wiki[self.i]

  def next_char(self):
    c1=self.current_char()
    if c1!="eof":
      self.i+=1    
      try:        
        if self.current_char()=='\r':
          try:
            c=self.wiki[self.i+1]
            if c=='\n':
              self.i+=1         
          except:
            pass        
        c2=self.current_char()
        self.deb_ligne=(c1=='\n' or (self.deb_ligne and ((c1 in [":","*","#"]) and (c2 in [":","*","#"]))))
      except:
        self.deb_ligne=False  

  def debut_ligne(self):
    return self.deb_ligne

  def save_pos(self):
    self.save_i=self.i
    self.save_deb=self.deb_ligne

  def restore_pos(self):
    self.i=self.save_i
    self.deb_ligne=self.save_deb



class Scanner:
  def __init__(self,wiki):
    """
      Initialise un objet Scanner avec le texte wiki
      scanne les tokens ssi self.nowiki==True
      self.nowiki passe à False dès que la balise self.end_nowiki_tag est rencontrée
    """
    self.reader=Reader(wiki)
    self.nowiki=False  
    self.end_nowiki_tag=""
    self.next_token()

  def set_nowiki_tag(self,end_tag):
    self.end_nowiki_tag=end_tag   
    self.nowiki=True
    self.occurences=1    

  def check_tag_complex(self,tag):
    """
      Vérifie que la balise tag est bien supportée
    """
    return tag in (title_tags+list_tags+pos_tags+format_tags+dont_parse_tags)

  def check_tag_single(self,tag):
    """
      Vérifie que la balise tag est bien supportée
    """
    return tag in single_tags_para+single_tags_not_para

  def read_nchar(self, c):
    """
      Renvoit le nombre d'occurence à la suite de c
    """
    count=0
    try:
      while self.reader.current_char()==c:
        count+=1
        self.reader.next_char()
    except:
      pass
    return count    

  def is_special(self,c):
    spec=["[","]","<",">","|","{","}","=","'","\n","eof"]
    deb_spec=[" ","*","#",":","!"]
    return (c in spec) or (self.reader.debut_ligne() and (c in deb_spec))     

    
  def is_letter(self,c):
    return ("a"<=c and c<="z") or ("A"<=c and c<="Z")

  
  def is_digit(self,c):
    return ("0"<=c and c<="9") 


  def read_string(self):
    """
      Lit et renvoit une suite de lettre ou de chiffres: utile pour les balises
    """
    s=""
    while self.is_digit(self.reader.current_char()) or\
          self.is_letter(self.reader.current_char()) or\
          self.reader.current_char()==" ":
      s+=self.reader.current_char()
      self.reader.next_char()
    return s.strip()
    
  def read_space(self):
    """
      Avance le Reader jusqu'au prochain caractère non espace ou saut de ligne
    """
    while self.reader.current_char()==" " or\
          self.reader.current_char()=="\n":
      self.reader.next_char()
  
  def read_until(self,l):
    """
      Lit une chaîne de caractère tant que l'on a pas rencontré le caractère c
      Gère les \n, \r, \t, \\, \" et \'
    """   
    s=""   
    while not self.reader.current_char() in l:
      if self.reader.current_char()=="\\":
        self.reader.next_char()
        if self.reader.current_char()=="n":
          s+="\n"
        elif self.reader.current_char()=="r":
          s+="\r"
        elif self.reader.current_char()=="t":
          s+="\t"                    
        elif self.reader.current_char()=="\\":
          s+="\\"
        elif self.reader.current_char()=="\"":
          s+="\""
        elif self.reader.current_char()=="\'":                  
          s+="\'"
        else:
          s+="\\"
          s+=self.reader.current_char()
      else:
        s+=self.reader.current_char()
      self.reader.next_char()
    return s  
    
  def read_tag(self):
    """
      Lit le contenu d'une balise:
    """
    tag=""
    args={}
    params=""  ## In case of an exception, the parametre is being read
               #en cas d'exception: le paramètre en train d'être lu
    end_str="" ## In case of an exception, the string is to add at the end
               #en cas d'exception: la chaîne à rajouter au bout
    single=False
    
    self.read_space()
    while self.is_letter(self.reader.current_char()) or\
          self.is_digit(self.reader.current_char()):
      tag+=self.reader.current_char()
      self.reader.next_char()
    while True:
      self.read_space()
      if self.is_letter(self.reader.current_char()):  
        params=self.read_string()
        self.read_space()
        if self.reader.current_char()=="=":
          self.reader.next_char()
          self.read_space()
          if self.reader.current_char()=="\"":
            self.reader.next_char()
            value=self.read_until(["\""])
          elif self.reader.current_char()=="\'":
            self.reader.next_char()
            value=self.read_until(["\'"])
          else:
            raise Exception
          args[params]=value
          self.reader.next_char()   
        else:
          raise Exception
      elif self.reader.current_char()==">":
        single=False
        break
      elif self.reader.current_char()=="/":
        self.reader.next_char()
        if self.reader.current_char()==">":
          single=True
          break
        else:
          raise Exception
      else:
        raise Exception
    return (tag,single,args)            

  def read_text(self):
    """
      Lit et renvoit une suite de caractères non spéciaux
    """    
    s=self.reader.current_char()
    self.reader.next_char()   
    try:
      while not self.is_special(self.reader.current_char()):
        s+=self.reader.current_char()
        self.reader.next_char()
    except:
      pass
    return s

  def current_token(self):
    """
      Renvoit le token courant
    """
    return self.t
  
  def next_token(self):
    """
      Stocke le prochain token
    """
    self.t=self.calc_next_token()


  def calc_next_token(self):
    """
      Renvoit le prochain token
    """
    c=self.reader.current_char()
    if c=="eof": return Token("eof",None)
    if self.reader.debut_ligne() and not self.nowiki:
      if c=="*": return Token("*",self.read_nchar(c))
      if c=="#": return Token("#",self.read_nchar(c))     
      if c==":": return Token(":",self.read_nchar(c))
      if c=="!":  
        self.reader.next_char()
        return Token("!",None)
      if c==" ":  
        self.reader.next_char()
        return Token("space",None)
      if c=="-":
        self.reader.save_pos()
        n=self.read_nchar(c)
        if n==4:
          return Token("tag","hr")
        else:
          s=""
          for i in range(0,n):
            s+="-"
          return Token("text",s)            

    if c=="\n" and not self.nowiki:  
      self.reader.next_char()
      return Token("return",None)
    if c=="\n" and self.nowiki:
      self.reader.next_char()
      return Token("tag","br")
    if c=="=" and not self.nowiki: 
      n=self.read_nchar(c)
      if 2<=n:
        return Token("=",n)
      else:
        s=""
        for i in range(0,n):
          s+="="
        return Token("text",s)
    if c=="'" and not self.nowiki:
      self.reader.save_pos()
      n=self.read_nchar(c)
      if 2<=n:
        return Token("'",n)
      else:
        s=""
        for i in range(0,n):
          s+="'"
        return Token("text",s)
    if c=="[" and not self.nowiki: 
      self.reader.next_char()  
      if self.reader.current_char()=="[":
        self.reader.next_char()
        return Token("[[",None)
      else:
        return Token("[",None)
    if c=="]" and not self.nowiki:
      self.reader.next_char()
      if self.reader.current_char()=="]":
        self.reader.next_char()
        return Token("]]",None)
      else:
        return Token("]",None)
    if c=="{" and not self.nowiki:
      self.reader.save_pos()
      self.reader.next_char()
      if self.reader.current_char()=="|":
        self.reader.next_char()
        return Token("{|",None)
      if self.reader.current_char()=="{":
        self.reader.next_char()
        return Token("{{",None)
      else:
        self.reader.restore_pos()
    if c=="}" and not self.nowiki:
      self.reader.save_pos()
      self.reader.next_char()
      if self.reader.current_char()=="}":
        self.reader.next_char()
        return Token("}}",None)
      else:
        self.reader.restore_pos()
    if c=="|" and not self.nowiki:
      self.reader.next_char()
      if self.reader.current_char()=="}":
        self.reader.next_char()
        return Token("|}",None)
      elif self.reader.current_char()=="-":
        self.reader.next_char()
        return Token("|-",None)
      elif self.reader.current_char()=="+":
        self.reader.next_char()
        return Token("|+",None)        
      elif self.reader.current_char()=="}":
        self.reader.next_char()
        return Token("|}",None)
      else:
        return Token("|",None)              
    if c=="<":
      self.reader.save_pos()
      self.reader.next_char()
      if self.reader.current_char()=="/":
        self.reader.next_char()
        text=self.read_string()
        if self.reader.current_char()==">":
          self.reader.next_char()                            
          if self.nowiki:               
            if text==self.end_nowiki_tag:
              self.occurences-=1
              if self.occurences==0:
                self.nowiki=False
                return Token("tag_close",text)
            return Token("text","</"+text+">")              
          else:              
            if self.check_tag_complex(text):
              return Token("tag_close",text)
            else:
              return Token("text","</"+text+">")
        else:
          self.reader.restore_pos()
      else:
        (tag,single,params)=self.read_tag()
        self.reader.next_char()       
        if not single:              
          if self.nowiki:
            if tag==self.end_nowiki_tag:
              self.occurences+=1
            self.reader.restore_pos()  
          else:                           
            if self.check_tag_complex(tag): 
              return Token("tag_open",tag,arg2=params)
            elif self.check_tag_single(tag):
              return Token("tag",tag,arg2=params)
            else:
              self.reader.restore_pos()
        else:                     
          if self.nowiki:
            if tag==self.end_nowiki_tag:
              self.occurences+=1
            self.reader.restore_pos()                    
          else:
            if self.check_tag_single(tag):                                      
              return Token("tag",tag,arg2=params)
            else:
              return Token("text","<"+text[:-1]+" />")
    return Token("text",self.read_text())


class Parser:
  def __init__(self,db,wiki):
    self.db=db
    self.wiki=wiki


  def generate(self):
    return self.parent.generate()

    

  def parse_wiki(self,check_links=False,generate_pdf=False,page_id="",chdir=None):
    """
      Parse le wiki en général
      - check_links: si vrai: vérifie les liens internes et renvoit les liens cassés sous la forme (pages, liens, images)
      - page_id: id de la page à parser, sert pour le répertoire où stocker la page
    """
    self.scanner=Scanner(self.wiki)
    self.parent=WikiTree("")
    self.sections=[self.parent,None,None,None,None]
    self.ul_dic={}
    self.ol_dic={}
    self.unknow_images=[]
    self.unknow_pages=[]
    self.unknow_links=[] 
    self.generated_latex=[] 
    self.check_links=check_links
    self.generate_pdf=generate_pdf
    self.page=page_id
    self.latex_dir=os.path.join(confstatic.latex_path,self.page)
        
    self.make_section(2,"")
   
    utils.mkdirp(self.latex_dir)
    (self.backgnd_cl,self.foregnd_cl) = utils.latex_colors(chdir=chdir)    

               
    while self.scanner.current_token().ttype!="eof":
      t=self.scanner.current_token()
      if t.ttype=="*":      
        self.parse_ul()        
      elif t.ttype=="#":
        self.parse_ol()
      elif t.ttype=="=":        
        self.parse_section()        
      elif t.ttype==":":
        self.parse_tab()
      elif t.ttype=="'":
        self.current.add(self.parse_para())
      elif t.ttype=="space":
        self.current.add(self.parse_code())
      elif t.ttype=="return":
        self.scanner.next_token()
        if self.scanner.current_token().ttype=="return":
          self.current.add(WikiTree("sbr",single=True))      
      elif t.ttype=="[":
        self.current.add(self.parse_para())        
      elif t.ttype=="[[":
        self.current.add(self.parse_para())  
      elif t.ttype=="{{":
        self.current.add(self.parse_exposant())  
      elif t.ttype=="{|":
        self.current.add(self.parse_array())
      elif t.ttype=="tag_open":
        if(t.arg in format_tags+list_tags+pos_tags+dont_parse_tags):
          self.current.add(self.parse_para())    
        else:
          self.current.add(self.parse_tag(all_tags))    
      elif t.ttype=="tag":
        self.current.add(self.parse_single_tag(single_tags_para+single_tags_not_para))         
      elif t.ttype=="text":      
        self.current.add(self.parse_para())       
      else:      
        texte=""
        if t.ttype=="]": texte="]"
        if t.ttype=="]]": texte="]]"
        if t.ttype=="|}": texte="|}"
        if t.ttype=="}}": texte="}}"
        if t.ttype=="|": texte="|"
        if t.ttype=="|-": texte="|-"
        if t.ttype=="!": texte="!"
        if t.ttype=="tag_close": texte="""</%s>"""%t.arg
        self.scanner.next_token()
        if len(self.current.node)>0:
          tree=self.current.node[-1]
          if tree.tag=="":
            if tree.node[-1].tag=="para":
              tree.node[-1].add(WikiTree("text",text=texte))
              self.parse_para(continue_with=tree)
            else:
              self.current.add(WikiTree("text",text=texte))
          else:        
            self.current.add(WikiTree("text",text=texte))
        else:        
          self.current.add(WikiTree("text",text=texte))       
        
    remove_all=True
    images=os.listdir(self.latex_dir)
    for img in images:
      if os.path.isfile(os.path.join(self.latex_dir,img)) and not img in self.generated_latex:
        os.remove(os.path.join(self.latex_dir,img))
      else:
        remove_all=False
    if remove_all:
      try:
        os.rmdir(self.latex_dir)
      except:
        pass

  def parse_str(self):
    """
      Concatène plusieurs token text en un seul
    """
    s=""    
    while self.scanner.current_token().ttype=="text":
      s+=self.scanner.current_token().arg
      self.scanner.next_token()
    return WikiTree("text",text=s)

  def parse_text(self,break_at_return=False,parse_format=True,preformated=False):
    """
      Parse du texte, en prenant en compte les balises de formatage.
      Tokens autorisés: text, ' et tag_open pour arg dans
      ["strike","u","br","i","b","highlight","big","small","math","sub","sup"]
    """
    tree=WikiTree("")
    while True:
      t=self.scanner.current_token()
      if t.ttype=="text":
        t=self.parse_str()       
        if len(t.node)!=0:
          tree.add(t)        
      elif t.ttype=="'" and parse_format:
        tree.add(self.parse_format())
      elif t.ttype=="[":
        tree.add(self.parse_link(False))        
      elif t.ttype=="[[":
        tree.add(self.parse_link(True))
      elif t.ttype=="{{":
        tree.add(self.parse_exposant())
      elif t.ttype=="tag_open":
        tree_tag=self.parse_tag(accept_tag=(format_tags+list_tags+pos_tags+dont_parse_tags))      
        if len(tree_tag.node)==0:
          break
        tree.add(tree_tag)
      elif t.ttype=="tag":
        tree_tag=self.parse_single_tag(accept_tag=single_tags_para)
        if len(tree_tag.node)==0:
          break        
        tree.add(tree_tag)        
      elif t.ttype=="return":
        if break_at_return:
          break
        else:
          self.scanner.next_token()
          t=self.parse_text(break_at_return=True)         
          if len(t.node)==0:
            if preformated:
              tree.add(WikiTree("text",text="\n"))          
            break
          else:
            if preformated:
              tree.add(WikiTree("text",text="\n"))
            else:
              tree.add(WikiTree("text",text=" "))
            tree.add(t)       
      else:
        break
    return tree
    

  def parse_para(self,parse_unique_para=False,preformated=False,continue_with=None):
    """
      Parse une suite de paragraphe.
    """
    if continue_with==None:
      root=WikiTree("")
    else:
      root=continue_with
    first_return=True
    while True:
      t=self.parse_text(preformated=preformated)
      if self.scanner.current_token().ttype=="return" or\
         self.scanner.current_token().ttype=="eof" and\
         not parse_unique_para and len(t.node)!=0: 
        if preformated:
          root.add(t)
          root.add(WikiTree("text",text="\n"))
        else:
          if continue_with==None:        
            tree=WikiTree("para")
            tree.add(t)
            root.add(tree)
          else:
            root.node[-1].add(t)
            continue_with=None
        self.scanner.next_token()
        while self.scanner.current_token().ttype=="return":
          if preformated:
            tree.add(WikiTree("text",text="\n"))
          else:
            tree.add(WikiTree("sbr",single=True))
          self.scanner.next_token()
      else:
        break  
    if len(t.node)!=0:
      if preformated:
        root.add(t)
      else:
        tree=WikiTree("para")
        tree.add(t)
        root.add(tree)
    return root



  def parse_code(self):
    """
      Parse les zones de code (lignes qui commencent par un espace)
    """
    self.scanner.next_token()        
    tree=WikiTree("synopsis")
    while True:
      if   self.scanner.current_token().ttype=="eof": break
      elif self.scanner.current_token().ttype=="return":
        self.scanner.next_token()
        if self.scanner.current_token().ttype=="space":
          tree.add(WikiTree("text",text="\n"))
          self.scanner.next_token()
        else:
          break
      else:
        t=self.parse_text(break_at_return=True)
        if len(t.node)==0:
          break
        else:
          tree.add(t)
    return tree
    

  def parse_single_tag(self,accept_tag):
    """
      Parse les balises contenues dans accept_tag
    """
    t=self.scanner.current_token()        
    if t.arg in accept_tag:
      self.scanner.next_token()     
      if t.arg == "br":
        return WikiTree("sbr", single=True)
      elif t.arg == "hr":
        return WikiTree("")
      elif t.arg == "module":   
        if t.arg2.has_key("id") and t.arg2["id"]!=confstatic.module_wiki_name:          
          args={}
          if t.arg2.has_key("params"):               
            params = t.arg2["params"].split("&")
                 
            for p in params:
              try:
                (key,value)=p.split("=")
                args[key]=value
              except:
                pass            
          if not t.arg2.has_key("page"):
            args["page"]=self.page
            mm = module_manager.ModuleManager(set=[False])
            mm.modules_mode = confstatic.mode
            mm.forward_lang(conf_general.language)
            try:
              mm[t.arg2["id"]]=t.arg2["id"]
              mm.forward_db_init(self.db)
              return WikiTree("text",text=mm[t.arg2["id"]].generate_content_xml(args),escape=False)
            except KeyError:
              pass
        s=""
        for k in t.arg2.keys():
          s+=" "
          s+=k
          s+="=\""
          s+=t.arg2[k]
          s+="\""       
        return WikiTree("text",text="""<%s%s />"""%(t.arg,s))
      else: 
        return WikiTree("text",text="""<%s />"""%(t.arg))
    else:
      return WikiTree("")


  def parse_tag(self,accept_tag):
    """
      Parse les balises contenues dans accept_tag
    """    
    t=self.scanner.current_token()
    if t.arg in accept_tag:   
       
      if t.arg in title_tags:
        self.scanner.next_token() 
        section=int(t.arg[1])
        texte=self.parse_text(break_at_return=True)
        t2=self.scanner.current_token()
        if t2.ttype=="tag_close" and t.arg==t2.arg:
          self.scanner.next_token()
          self.make_section(section,texte)
          return WikiTree("")           
        else:
          tree=WikiTree("")
          tree.add(WikiTree("text",text="""<%s>"""%(t.arg)))
          tree.add(texte)        
          return tree   
                 
      elif t.arg=="math":        
        size=confstatic.default_latex_dpi
        pack_str=""
        if t.arg2!=None:
          if t.arg2.has_key("size"):
            size=t.arg2["size"]
          if t.arg2.has_key("packages"):
            packages=t.arg2["packages"]            
            packages=filter(lambda p: len(p)!=0,packages.split(" "))            
            if len(packages)==0:
              pack_str=""
            else:
              pack_str=" -p "+packages[0]
              for p in packages[1:]:
                pack_str+=","
                pack_str+=p          
                  
        self.scanner.set_nowiki_tag("math")
        self.scanner.next_token()
        latex=WikiTree("")
        while True:
          t=self.scanner.current_token()
          if t.ttype=="eof": break
          if t.ttype=="tag_close" and t.arg=="math": break
          if t.ttype=="tag" and t.arg=="br":
            latex.add(WikiTree("text",text="\n"))
            self.scanner.next_token()
          else:
            texte=self.parse_text()
            latex.add(texte)               
        hash_md5_latex=hashlib.md5(latex.generate()).hexdigest()  
        hash_md5_params=hashlib.md5(size+pack_str).hexdigest()                            
        hash_md5=hashlib.md5(hash_md5_latex+hash_md5_params+self.backgnd_cl+self.foregnd_cl).hexdigest()             
        if not os.path.exists(os.path.join(self.latex_dir,hash_md5+".png")): 
          if self.backgnd_cl == "transparent":
            bgopt = "-T"
          else:
            bgopt = "-b '%s'" % self.backgnd_cl
            
          directory=os.getcwd()
          os.chdir(self.latex_dir)            
          c = """%s%s %s -f '%s' -i '$%s$' -o '%s' -d %s"""%(os.path.join(directory,confstatic.l2p_path),pack_str,bgopt,self.foregnd_cl, latex.generate(escape=False,escapeLatex=True),hash_md5+".png",size)
          os.system(c)
          os.chdir(directory)
        self.generated_latex.append(hash_md5+".png")
        self.scanner.next_token()        
        mediaobj=WikiTree("inlinemediaobject")              
        imageobj=WikiTree("imageobject")
        mediaobj.add(imageobj)
        imageobj.add(WikiTree("imagedata",args=[("fileref",confstatic.get_latex_url(self.page,hash_md5+".png"))],single=True))
        texteobj=WikiTree("textobject")      
        mediaobj.add(texteobj)      
        phrase=WikiTree("phrase")
        texteobj.add(phrase)
        phrase.add(WikiTree("text",text=latex.generate()))  
        return mediaobj
        
      elif t.arg=="nowiki":
        self.scanner.set_nowiki_tag("nowiki")     
        self.scanner.next_token()
        tree=WikiTree("")
        while True:
          t=self.scanner.current_token()
          if t.ttype=="eof": break
          if t.ttype=="tag_close" and t.arg=="nowiki": break
          if t.ttype=="tag" and t.arg=="br":
            tree.add(WikiTree("sbr",single=True))
            self.scanner.next_token()
          else:
            texte=self.parse_text()
            tree.add(texte)      
        self.scanner.next_token()          
        return tree  
            
      elif t.arg in (pos_tags):
        self.scanner.next_token()
        texte=self.parse_text()
        if self.scanner.current_token().ttype=="tag_close" and\
           self.scanner.current_token().arg=="center":
          self.scanner.next_token()
          tree=WikiTree("emphasis",[("role","centered")])
          tree.add(texte)
          return tree
        else:
          tree=WikiTree("")
          tree.add(WikiTree("text",text="""<%s>"""%(t.arg)))
          tree.add(texte)        
          return tree     
               
      elif t.arg in (format_tags+list_tags+pos_tags):
        self.scanner.next_token()
        if t.arg=="pre":
          texte=WikiTree("")
          while True:
            if self.scanner.current_token().ttype=="return":
              texte.add(WikiTree("text",text="\n"))
              self.scanner.next_token()
            else:
              txt=self.parse_text(preformated=True)
              if len(txt.node)==0:
                break
              else:
                texte.add(txt)          
        else:      
          texte=WikiTree("")
          while True:
            if self.scanner.current_token().ttype=="return":
              texte.add(WikiTree("sbr",single=True))
              self.scanner.next_token()
            else:
              txt=self.parse_text()
              if len(txt.node)==0:
                break
              else:
                texte.add(txt)
        t2=self.scanner.current_token()
        if t2.ttype=="tag_close" and t.arg==t2.arg:
          Wiki2DocBook= {\
            "s"   : ("emphasis",[("role","strikethrough")]),\
            "highlight": ("emphasis",[("role","highlight")]),\
            "u": ("emphasis",[("role","underline")]),\
            "b": ("emphasis",[("role","strong")]),\
            "i": ("emphasis",None),\
            "pre": ("synopsis",None),\
            "big": ("emphasis",[("role","bigtext")]),\
            "small": ("emphasis",[("role","smalltext")]),\
            "sub": ("subscript",None),\
            "sup": ("superscript",None),\
            "ul": ("itemizedlist",None),\
            "ol": ("orderedlist",None),\
            "li": ("listitem",None),\
            "ref": ("footnote",None)   
          }                                                                                               
          self.scanner.next_token()
          param=Wiki2DocBook[t.arg]
          tree=WikiTree(param[0],args=param[1])
          if t.arg=="ref":
            para=WikiTree("para")
            para.add(texte)
            texte=para
          tree.add(texte)
          return tree
        else:
          tree=WikiTree("")
          tree.add(WikiTree("text",text="""<%s>"""%(t.arg)))
          tree.add(texte)        
          return tree
      else: 
        return WikiTree("text",text="""<%s>"""%(t.arg))
    else:
      return WikiTree("")                                                    


  def parse_array(self):
    """
      Parse les tableaux
    """
    root=WikiTree("table",args=[("frame","all")])
    title=WikiTree("title")
    root.add(title)
    tgroup=WikiTree("tgroup",args=[("align","left"),("colsep","1"),("rowsep","1")])
    root.add(tgroup)
    colspec=WikiTree("")
    tgroup.add(colspec)
    tree=WikiTree("tbody")
    tgroup.add(tree)
    row=None
    current_col=-1
    max_col=-1
    self.scanner.next_token()
    while self.scanner.current_token().ttype!="|}":
      t=self.scanner.current_token()
      if t.ttype=="|+":
        self.scanner.next_token()
        texte=self.parse_text()
        title.add(texte)         
      elif t.ttype=="|-":
        current_col=-1
        row=WikiTree("row")
        tree.add(row)
        self.scanner.next_token()  
      elif t.ttype=="|" or t.ttype=="!":      
        if row==None:
          current_col=-1
          row=WikiTree("row")
          tree.add(row)
        current_col+=1
        if current_col>max_col:
          max_col+=1
          colspec.add(WikiTree("colspec",single=True,args=[("colname","c"+str(max_col))]))
        self.scanner.next_token()
        texte=self.parse_text(break_at_return=True)
        if self.scanner.current_token().ttype=="|":
          try:
            options=[]
            args=[]
            if texte.tag=="text":
              args+=texte.node.split(" ")
            else:
              for t in texte.node:
                if t.tag=="text":
                  args+=t.node.split(" ")
                else:
                  args+=t.generate().split(" ")
            for a in args:
              try:
                (arg,value)=a.split("=")
                if value[0]=="\"" or value[0]=="\'":
                    value=value[1:-1]
                if arg=="align" and (value=="left" or value=="center" or value=="right" or value=="justify"):
                  options.append(("align",value))
                if arg=="valign" and (value=="top" or value=="middle" or value=="bottom"):
                  options.append(("valign",value))                  
                elif arg=="colspan":
                  if int(value)>1:
                    options.append(("namest","c"+str(current_col)))
                    options.append(("nameend","c"+str(current_col+int(value)-1)))   
                elif arg=="rowspan":
                  if int(value)>1:
                    options.append(("morerows",str(int(value)-1)))                  
              except:
                pass   
            self.scanner.next_token()
            texte=WikiTree("")
            if self.scanner.current_token().ttype=="return":
              self.scanner.next_token()              
            else:
              texte.add(self.parse_text(break_at_return=True))   
            while True:
              while self.scanner.current_token().ttype=="return":
                texte.add(WikiTree("sbr",single=True))
                self.scanner.next_token()
              t=self.parse_text()
              if len(t.node)==0:
                break
              else:
                texte.add(t)
            if options==[]:
              options=None
            entry=WikiTree("entry",args=options)
            entry.add(texte)
            row.add(entry)            
          except:
            self.scanner.next_token()  
        else:
          txt=WikiTree("")
          txt.add(texte)
          if self.scanner.current_token().ttype=="return":
            t=self.parse_text()
            if len(t.node)!=0:
              txt.add(WikiTree("sbr",single=True))
              while True:
                while self.scanner.current_token().ttype=="return":
                  txt.add(WikiTree("sbr",single=True))
                  self.scanner.next_token()
                t=self.parse_text()
                if len(t.node)==0:
                  break
                else:
                  txt.add(t)
            
          entry=WikiTree("entry")
          entry.add(txt)
          row.add(entry)
      elif t.ttype=="return":
        self.scanner.next_token()
      else:
        if len(self.parse_text().node)==0:
          return root
    tgroup.args.append(("cols",str(max_col+1)))    
    self.scanner.next_token()
    return root
    
  


  def make_section(self, sect_nbr, texte, n=[0]):
    """
      Gère le découpage en section
      sect_nbr compris entre 2 et 5
    """
    tree=WikiTree("sect"+str(sect_nbr-1))
    if not self.generate_pdf:
      id_tree=WikiTree("idComfort")
      id_tree.add(WikiTree("text",text=confstatic.module_wiki_name+str(n[0]))) 
      tree.add(id_tree)         
      n[0] = n[0]+1
    if texte != "":    
      title=WikiTree("title")
      title.add(texte)
      tree.add(title)        
    elif self.generate_pdf:
      title=WikiTree("title")
      title.add(WikiTree("text",text=self.page))
      tree.add(title)    
    self.sections[sect_nbr-2].add(tree)
    self.current=tree
    for i in range(sect_nbr-1,4):
      self.sections[i]=tree



  def parse_section(self):
    """
      Parse les tokens ==, ===, ====, =====
      et dispatche en section
    """
    n1=self.scanner.current_token().arg
    self.scanner.next_token()
    text=self.parse_text(break_at_return=True)        
    if len(text.node)!=0:
      if n1>6:
        buff=WikiTree("")
        string=""
        for i in range(6,n1):
          string+="="
        n1=6
        buff.add(WikiTree("text",text=string))
        buff.add(text)
        text=buff
        
      if self.scanner.current_token().ttype=="=":
        if n1<self.scanner.current_token().arg:
          string=""
          for i in range(n1,self.scanner.current_token().arg):
            string+="="
          self.scanner.current_token().arg=n1
          text.add(WikiTree("text",text=string))
        if n1>self.scanner.current_token().arg:
          buff=WikiTree("")
          string=""
          for i in range(self.scanner.current_token().arg,n1):
            string+="="
          n1=self.scanner.current_token().arg
          buff.add(WikiTree("text",text=string))
          buff.add(text)
          text=buff              
        self.make_section(n1,text)
        self.scanner.next_token()
        if self.scanner.current_token().ttype=="return":
          self.scanner.next_token()        
      else:
        t=WikiTree("")
        string=""
        for i in range(0,n1):
          string+="="         
        t.add(WikiTree("text",text=string))
        t.add(text)
        if self.scanner.current_token().ttype=="return":
          t.add(WikiTree("text",text=" "))
          self.scanner.next_token()         
        self.current.add(t)
    else:
      t=WikiTree("text",text="")
      for i in range(0,n1):
        t.add("=")
      self.current.add(t)


  def parse_format(self):
    """
      Parse la mise en forme via les token '', ''' et '''''s
    """
    t=self.scanner.current_token()
    self.scanner.next_token()
    text=self.parse_text(break_at_return=True,parse_format=False)
    
    if t.arg==4:
      buff=WikiTree("")
      text.node=[WikiTree("text",text="'")]+text.node
      t.arg=3
    if t.arg>5:
      string=""
      for i in range(5,t.arg):
        string+="'"
      text.node=[WikiTree("text",text=string)]+text.node
      t.arg=5
      
    if self.scanner.current_token().ttype=="'":
      if self.scanner.current_token().arg==4:
        text.node.append(WikiTree("text",text="'"))
        self.scanner.current_token().arg=3
      if t.arg<self.scanner.current_token().arg:
        string=""
        for i in range(t.arg,self.scanner.current_token().arg):
          string+="'"
        text.node.append(WikiTree("text",text=string))
        self.scanner.current_token().arg=t.arg
      if t.arg>self.scanner.current_token().arg:
        string=""
        for i in range(self.scanner.current_token().arg,t.arg):
          string+="'"
        text.node=[WikiTree("text",text=string)]+text.node
        t.arg=self.scanner.current_token().arg      

      self.scanner.next_token()
      if t.arg==2:    
        tree=WikiTree("emphasis")
        tree.add(text)
        return tree
      elif t.arg==3:
        tree=WikiTree("emphasis",args=[("role","strong")])
        tree.add(text)
        return tree
      else:
        treeb=WikiTree("emphasis",args=[("role","strong")])
        treei=WikiTree("emphasis")
        treei.add(text)
        treeb.add(treei)
        return treeb
    else:
      string=""
      for i in range(0,t.arg):
        string+="'"
      text.node=[WikiTree("text",text=string)]+text.node
      return text


  def parse_ul(self):
    """
      Parse les *
    """
    level=self.scanner.current_token().arg
    tree_root=None
    for ul in self.ul_dic.keys():
      if ul>level:
        self.ul_dic[ul]=None
      elif ul==level:
        tree_root=self.ul_dic[ul]
    if tree_root==None:
      tree_root=WikiTree("itemizedlist")
      self.ul_dic[level]=tree_root      
      last_current=self.current
      self.current.add(tree_root)
      self.current=tree_root      
    else:
      last_current=None
    tree=WikiTree("listitem")
    tree_root.add(tree)
    self.current=tree    
    self.scanner.next_token()
    
    parsed_para=False
    while True:
      t=self.scanner.current_token()
      if t.ttype=="*":     
        self.parse_ul() 
        break          
      elif t.ttype=="#" and not parsed_para:
        self.parse_ol()
        break
      elif t.ttype==":":
        self.parse_tab()        
      else:
        if not parsed_para:
          t=self.parse_para(parse_unique_para=True)              
          if len(t.node)==0:
            break
          else:
            if self.scanner.current_token().ttype=="return":
              parsed_para=True
            tree.add(t)
        else:
          break

    if last_current!=None:
      self.ul_dic[level]=None
      self.current=last_current


  def parse_ol(self):
    """
      Parse les #
    """ 
    level=self.scanner.current_token().arg
    tree_root=None
    for ol in self.ol_dic.keys():
      if ol>level:
        self.ol_dic[ol]=None
      elif ol==level:
        tree_root=self.ol_dic[ol]
    if tree_root==None:
      tree_root=WikiTree("orderedlist")
      self.ol_dic[level]=tree_root
      last_current=self.current
      self.current.add(tree_root)
    else:
      last_current=None      
    tree=WikiTree("listitem")
    tree_root.add(tree)
    self.current=tree
    self.scanner.next_token()
    
    parsed_para=False
    while True:
      t=self.scanner.current_token()
      if t.ttype=="*" and not parsed_para:
        self.parse_ul()
        break
      elif t.ttype=="#":
        self.parse_ol()
        break        
      elif t.ttype==":":
        self.parse_tab()       
      else:
        if not parsed_para:
          t=self.parse_para(parse_unique_para=True)
          if len(t.node)==0:
            break
          else:
            if self.scanner.current_token().ttype=="return":
              parsed_para=True            
            tree.add(t)
        else:
          break          

    if last_current!=None:
      self.ol_dic[level]=None
      self.current=last_current

  def parse_tab(self):
    """
      Parse les :
    """
    self.scanner.next_token()



  def make_link(self,fields,internal):
    """
      Insère un lien ou une image
    """
    image=False
    type_link=0 ## 0 - normal link # 0 - lien normal
                ## 1 - link to ./perso/docs     # 1 - lien vers ./perso/docs
                ## 2 - link to ./perso/pages    # 2 - lien vers ./perso/pages
                ## 3 - link to ./perso/pictures # 3 - lien vers ./perso/pictures
    try:
      i = fields[0].index(":")
      prefixe=fields[0][:i]
      if prefixe=="Image":
        image=True
        fields[0]=fields[0][i+1:]
      elif internal:
        if prefixe=="Doc":
          type_link=1
          fields[0]=fields[0][i+1:]
        elif prefixe=="Page":
          type_link=2
          fields[0]=fields[0][i+1:]
        elif prefixe=="Picture":
          type_link=3
          fields[0]=fields[0][i+1:]                
    except:
      pass
    fields[0]=fields[0].strip()
    if image:
      if internal:
        url=confstatic.get_pictures_url(fields[0])
        if self.check_links:
          if not os.path.exists(url):
            self.unknown_images.append(url)
      else:
        url=fields[0]
      thumb=False
      align=""
      sizetype=0 ## 0 - Unspecified  
                 ## 1 - MaxSize: 200px
                 ## 2 - Width*Height:    200x150px
                 #  0 - non spécifié
                 #  1 - MaxSize: 200px
                 #  2 - Largeur*Hauteur: 200x150px
      size=0
      width=0
      height=0
      field=1
      title=""    
      try:
        while True:
          fields[field]=fields[field].strip()
          if fields[field]=="thumb":
            thumb=True            
          elif fields[field]=="left" or fields[field]=="center" or fields[field]=="right":
            align=fields[field]                 
          else:
            try:
              size=int(fields[field])
              sizetype=1
              field+=1
            except:
              try:
                index=fields[field].index("px")
                s=(fields[field][:index]).split("x")
                if len(s)==1:
                  size=int(s[0])
                  sizetype=1
                  field+=1
                if len(s)==2:
                  width=int(s[0])
                  height=int(s[1])
                  sizetype=2
                  field+=1
              except:
                title=fields[field]            
          field+=1      
      except:
        pass
      options=[("fileref",url)]
      if sizetype==0:
        if thumb:
          options.append(("width","180px"))  
          options.append(("depth","180px"))
          options.append(("scalefit","1"))
      elif sizetype==1:   
          options.append(("width",str(size)+"px"))  
          options.append(("depth",str(size)+"px"))
          options.append(("scalefit","1"))
      elif sizetype==2:
          options.append(("contentwidth",str(width)+"px"))  
          options.append(("contentdepth",str(height)+"px"))
      if align!="":
        options.append(("align",align))
      mediaobj=WikiTree("inlinemediaobject")
      imageobj=WikiTree("imageobject")
      mediaobj.add(imageobj)
      imageobj.add(WikiTree("imagedata",args=options,single=True))
      if title!="":
        texteobj=WikiTree("textobject")      
        mediaobj.add(texteobj)      
        phrase=WikiTree("phrase")
        texteobj.add(phrase)
        phrase.add(WikiTree("text",text=title))  
      return mediaobj
    else:
      if internal:  
        if type_link==0:
          url=confstatic.build_url({"page":fields[0]+".html"})
          if self.check_links:
            try:
              self.db.table(confstatic.pages_database_prefix). select(("page_id","=",fields[0])).next()
            except:
              self.unknown_pages.append(url)             
        else:
          if type_link==1:
            url=confstatic.get_docs_url(fields[0])
          elif type_link==2:
            url=confstatic.get_pages_url(fields[0])
          else:
            url=confstatic.get_pictures_url(fields[0])
          if self.check_links:
            if not os.path.exists(url):
              self.unknown_links.append(url)  
        
      else:
        url=fields[0]
      link=WikiTree("ulink",args=[("url",url)])
      if len(fields)!=1:
        link.add(WikiTree("text",text=fields[1]))
      else:
        link.add(WikiTree("text",text=fields[0]))
      return link


  def parse_link(self,internal):
    self.scanner.next_token()
    fields=[]
    while True:
      t=self.scanner.current_token()
      if t.ttype=="eof": break
      elif t.ttype=="]]" and internal: break
      elif t.ttype=="]" and not internal: break      
      elif t.ttype=="return": break
      elif t.ttype=="|":
        self.scanner.next_token()
      else:
        field=self.parse_str()
        if len(field.node)==0:
          break
        else:
          fields.append(field.generate())
    if (internal and self.scanner.current_token().ttype!="]]") or (not internal and self.scanner.current_token().ttype!="]") or len(fields)==0:
      tree=WikiTree("")
      if internal:
        tree.add(WikiTree("text",text="[["))
      else:
        tree.add(WikiTree("text",text="["))
      if len(fields)!=0:
        tree.add(WikiTree("text",text=fields[0]))
      for f in fields[1:]:
        tree.add(WikiTree("text",text="|"))
        tree.add(WikiTree("text",text=f))
      return tree
    else:
      self.scanner.next_token()
      return self.make_link(fields,internal)

      
      
  def parse_exposant(self):
    self.scanner.next_token()
    if self.scanner.current_token().ttype=="text":
      exp_ind=self.parse_text()     
      if self.scanner.current_token().ttype=="|":
        self.scanner.next_token()
        if self.scanner.current_token().ttype=="text":
          texte=self.parse_text()
          if self.scanner.current_token().ttype=="}}":
            if exp_ind.node=="ind":
              tree=WikiTree("subscript")
              tree.add(texte)
              self.scanner.next_token()
              return tree
            elif exp_ind.node=="exp":
              tree=WikiTree("superscript")
              tree.add(texte)
              self.scanner.next_token()
              return tree            
            else:
              tree=WikiTree("")
              tree.add(WikiTree("text",text="{{"))
              tree.add(exp_ind)
              tree.add(WikiTree("text",text="|"))
              tree.add(texte)
              return tree            
          else:
            tree=WikiTree("")
            tree.add(WikiTree("text",text="{{"))
            tree.add(exp_ind)
            tree.add(WikiTree("text",text="|"))
            tree.add(texte)
            return tree
      elif self.scanner.current_token().ttype=="}}":
        tree=WikiTree("superscript")
        tree.add(exp_ind)
        self.scanner.next_token()
        return tree            
      else:
        tree=WikiTree("")
        tree.add(WikiTree("text",text="{{"))
        tree.add(exp_ind)
        return tree       
    else:
      return WikiTree("text",text="}}") 



class TheModule(ComfortModule, IModuleContentProvider, IModuleDB):
  mode = "both"

  def module_init(self):
    pass

  def module_title(self):
    return ""

  def module_name(self):
    return confstatic.module_wiki_name

  def module_id(self):
    return "Wiki"

  def init_content(self):
    pass

  def setup_db(self, db):
    self.db=db

  def generate_content_xml(self, args):
    args2=args.copy() 
    try:
      i=args2["page"].rindex(".html")
      args2["page"]=args2["page"][:i]
    except:
      pass
    page=self.db.table(confstatic.pages_database_prefix).select(cond=[("page_id","=",args2["page"])]).next()
    if page["page_wiki"]==None:
      p=Parser(self.db,"") 
    else:
      p=Parser(self.db,page["page_wiki"])    
    try:
      pdf=(args["pdf"]=="1")
    except:
      pdf=False
    p.parse_wiki(generate_pdf=pdf,page_id=args2["page"]) 
    return p.generate()

##????
## Title on many lines, paste it back?
## Code on many lignes --> only one marker synopsis?
#????
#Titre sur plusieurs lignes: le recoller?
# code sur pls lignes --> une seule balise synopsis?
