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
    La classe Token contient deux variables: t (le type du token), arg (le nombre d'arguments)
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
  def __init__(self,t,arg):
    self.t=t 
    self.arg=arg

class WikiTree:
  """
    Arbre d'interprétation pour le wiki
      - self.tag indique la balise docbook correspondante
      - self.node est la liste des arbres inclus entre la balise ouvrante
        et fermante si self.tag!="text", le texte sinon
      - self.args: une liste de couple (paramètre XHTML de la balise, valeur)
  """
  def __init__(self, tag, args=[], text=None, single=False, escape=True):
    self.tag=tag
    self.args=args
    self.escape=escape
    self.single=single
    if self.tag=="text":
      self.node=text  ## A leaf of the tree #une feuille de l'arbre
    else:
      self.node=[]    ## A node of the tree #un noeud de l'arbre
      
  def add(self,tree):
    if self.tag=="text":
      self.node+=tree
    else:
      self.node.append(tree)

  def escape_str(self,string):
    """
      " and ' are transformed into \\" and \\'
      on transforme les " et ' en \\" et \\'
    """
    s=""
    for c in string:
      if   c=='\"': s+="\\\""
      elif c=='\'': s+="\\\'"
      else: s+=c
    return s
  
  def escape_special(self,string):
    """
      <,>," and & are transformed into HTML code
      on transforme les <, >, " et & en code HTML
    """
    s=""
    for c in string:
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
  
  def escape_latex(self,string):
    """
      ' are transformed into \\textquoteright
      on transforme les ' en \\textquoteright
    """
    s=""
    last=""
    for c in string:
      if c=="\'":
        if last=="\\":
          s+=" "          
        s+="\\textquoteright "
      else:
        s+=c
      last=c         
    return s

  def generate(self,escape=True,escapeLatex=False):
    escape=self.escape and escape
    if self.tag=="text":
      if escape:         return self.escape_special(self.node)
      elif escapeLatex:  return self.escape_latex(self.node)
      else:              return self.node  
    else:
      s=""
      if self.tag!="":        
        args=""
        for a in self.args:
          args+="""%s=\"%s\" """%(a[0],self.escape_str(a[1]))  
        if self.single:  
          s="""<%s %s/>"""%(self.tag,args)
        else:
          s="""<%s %s>"""%(self.tag,args)
      for t in self.node:
        s+=t.generate(escape=escape,escapeLatex=escapeLatex)
      if not self.single and self.tag!="":
        s+="""</%s>"""%(self.tag)
      return s

class Reader:
  """
    Contient le texte wiki
  """
  def __init__(self,wiki):
    self.wiki=wiki
    self.i=0;
    self.max=len(wiki)
    self.deb_ligne=True
    self.save_i=[]
    self.save_deb=[]
  
  def current_char(self):
    if self.i>=self.max:
      return "eof"
    else:
      return self.wiki[self.i]

  def next_char(self):
    c1=self.current_char()
    if c1!="eof":
      self.i+=1        
      if self.current_char()=='\r':
        try:
          c=self.wiki[self.i+1]
          if c=='\n':
            self.i+=1         
        except:
          pass        
      c2=self.current_char()
      self.deb_ligne=(c1=='\n' or (self.deb_ligne and ((c1 in [":","*","#"]) and (c2 in [":","*","#"]))))

  def debut_ligne(self):
    return self.deb_ligne

  def save_pos(self):
    self.save_i.append(self.i)
    self.save_deb.append(self.deb_ligne)

  def restore_pos(self):
    self.i=self.save_i.pop()
    self.deb_ligne=self.save_deb.pop()
    
  def clear_pos(self):
    self.save_i.pop()
    self.save_deb.pop()



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

  def read_nchar(self, c, maxi=0):
    """
      Renvoit le nombre d'occurence à la suite de c
    """
    count=0
    while self.reader.current_char()==c and count<maxi:
      count+=1
      self.reader.next_char()
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
      Lit une chaîne de caractère tant que l'on a pas rencontré un caractère de la liste l
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
    self.reader.next_char()
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
    if c=="eof": return Token("eof",[])
    if not self.nowiki:
      if self.reader.debut_ligne():
        if c=="*": return Token("*",[self.read_nchar(c)])
        if c=="#": return Token("#",[self.read_nchar(c)])     
        if c==":": return Token(":",[self.read_nchar(c)])
        if c=="!":  
          self.reader.next_char()
          return Token("!",[])
        if c==" ":  
          self.reader.next_char()
          return Token("space",[])
        if c=="-":
          n=self.read_nchar(c,maxi=4)
          if n==4: return Token("tag",["hr"])
          else:
            s=""
            for i in range(0,n):
              s+="-"
            return Token("text",[s])            
            
      if c=="\n":  
        self.reader.next_char()
        return Token("return",[])
      if c=="=": 
        n=self.read_nchar(c,maxi=6)
        if n!=1: return Token("=",[n])
        else:    return Token("text",["="])
      if c=="'":
        n=self.read_nchar(c,maxi=3)
        if n!=1: return Token("'",[n])
        else:    return Token("text",["'"])
      if c=="[": 
        self.reader.next_char()  
        if self.reader.current_char()=="[":
          self.reader.next_char()
          return Token("[[",[])
        else:
          return Token("[",[])
      if c=="]":
        self.reader.next_char()
        if self.reader.current_char()=="]":
          self.reader.next_char()
          return Token("]]",[])
        else:
          return Token("]",[])
      if c=="{":
        self.reader.save_pos()
        self.reader.next_char()
        if self.reader.current_char()=="|":
          self.reader.clear_pos()
          self.reader.next_char()
          return Token("{|",[])
        if self.reader.current_char()=="{":
          self.reader.clear_pos()
          self.reader.next_char()       
          return Token("{{",[])
        else:
          self.reader.restore_pos()
      if c=="}":
        self.reader.save_pos()
        self.reader.next_char()
        if self.reader.current_char()=="}":
          self.reader.clear_pos()
          self.reader.next_char()
          return Token("}}",[])
        else:
          self.reader.restore_pos()
      if c=="|":
        self.reader.next_char()
        if self.reader.current_char()=="}":
          self.reader.next_char()
          return Token("|}",[])
        elif self.reader.current_char()=="-":
          self.reader.next_char()
          return Token("|-",[])
        elif self.reader.current_char()=="+":
          self.reader.next_char()
          return Token("|+",[])        
        elif self.reader.current_char()=="}":
          self.reader.next_char()
          return Token("|}",[])
        else:
          return Token("|",[])         
                 
    if c=="<":
      self.reader.save_pos()
      self.reader.next_char()
      if self.reader.current_char()=="/":
        self.reader.next_char()
        tag=self.read_string()
        if self.reader.current_char()==">":
          self.reader.clear_pos()
          self.reader.next_char()                            
          if self.nowiki:               
            if tag==self.end_nowiki_tag:
              self.occurences-=1
              if self.occurences==0:
                self.nowiki=False
                return Token("tag_close",[tag])
              else: 
                return Token("text",["</"+tag+">"])              
          else:              
            if self.check_tag_complex(tag):
              return Token("tag_close",[tag])
            else:
              return Token("text",["</"+tag+">"])
        else:
          self.reader.restore_pos()
      else:
        try:
          (tag,single,params)=self.read_tag()              
          if self.nowiki:
            if tag==self.end_nowiki_tag:
              self.occurences+=1
            self.reader.restore_pos()  
          else:                                 
            if not single and self.check_tag_complex(tag): 
              self.reader.clear_pos()
              return Token("tag_open",[tag,params])
            elif single and self.check_tag_single(tag):   
              self.reader.clear_pos()                                   
              return Token("tag",[tag,params])
            else:
              self.reader.restore_pos()
        except:
          self.reader.restore_pos()
    return Token("text",[self.read_text()])



class Parser:
  """
    Parse le wiki
  """
  def __init__(self,db,wiki):
    self.db=db
    self.wiki=wiki
    self.scanner=Scanner(wiki)


  def generate(self):
    return self.parent.generate()

    

  def parse_wiki(self,check_links=False,generate_pdf=False,page_id="",chdir=None):
    """
      Parse le wiki en général
      - check_links: si vrai: vérifie les liens internes et renvoit les liens cassés sous la forme (pages, liens, images)
      - page_id: id de la page à parser, sert pour le répertoire où stocker la page
    """
    self.parent=WikiTree("")
    section=WikiTree("")
    self.parent.add(section)
    self.sections=[section,None,None,None,None]
    self.ul_dic={}
    self.ol_dic={}
    self.unknow_images=[]
    self.unknow_pages=[]
    self.unknow_links=[] 
    self.generated_latex=[] 
    self.check_links=check_links
    self.generate_pdf=generate_pdf
    self.latex_dir=os.path.join(confstatic.latex_path,page_id)
        
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
    pageId=args["page"]
    try:
      i=pageId.rindex(".html")
      pageId=page_id[:i]
    except ValueError:
      pass
    page=self.db.table(confstatic.pages_database_prefix).select(cond=[("page_id","=",pageId)]).next()
    if page["page_wiki"]==None:
      p=Parser(self.db,"") 
    else:
      p=Parser(self.db,page["page_wiki"])    
    try:
      pdf=(args["pdf"]=="1")
    except:
      pdf=False
    p.parse_wiki(generate_pdf=pdf,page_id=pageId) 
    return p.generate()

