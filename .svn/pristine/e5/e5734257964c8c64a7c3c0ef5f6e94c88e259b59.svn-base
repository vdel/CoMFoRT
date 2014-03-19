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
from xml.dom import minidom
from os import rename
from encode import EncodeToWrite, DecodeReading

## General scheme of a table
## List of dictionnaries
## The first is the field descriptor
## Others are records
# schéma général d'une table
# liste de dictionnaire
# le premier est le descripteur des champs, les
# autres sont les enregistrements.

## There will be a configuration file
# on aura un fichier de configuration


## Changes  "t1,t2,t3" into ["t1","t2","t3"]
# transforme "t1,t2,t3" en ["t1","t2","t3"]
def analyse(s):
  tmp = ""
  a = []
  for c in s:
    if c == ',':
      a.append(tmp)
      tmp = ""
    else:
      tmp = tmp + c
  a.append(tmp)
  return a

## tabs and line jumps before and after the string are removed  
# on enlève les tab et saut de ligne avant et après une chaine de caractère
def clean_string(s):
  begin = 0
  l = len(s)
  for i in range(l):
    if s[i] != "\t" and s[i] != "\n" and s[i] != " ":
      begin = i
      break
  for j in range(l):
    if s[l-j-1] != "\t" and s[l-j-1] != "\n" and s[l-j-1] != " ":
      end = l-j
      break
  return s[begin:end]

def date(s):
  return s

## value is to be return in the pattern type ["field"]
# on doit retourner value dans le type de schema["field"]
def typage(schema,field,chaine_value):
  ## Definition of an (action <=> C switch case) dictionnary
  # on définit un dico d'action <=> switch case en C
  actions = {}
  actions["text"] = str
  actions["int"] = int
  actions["date"] = date
  actions["id"] = int
  return actions[schema[field]](chaine_value)

## Takes a chilNodes child list and flatten its content in order
## to get everything that lies between two xml markers
# on prend une liste childNodes child et on concatène son contenu
# dans le but d'obtenir tout ce qui se trouve entre deux balises xml
def getAllChildrenContent(child):
  s = ""
  for i in child:
    s += i.toxml()
  return s



class xmlReader:
  """ fonction de parsage du fichier xml"""
  def __init__(self,name):
    self.xmldoc = minidom.parse(name)
    self.table = self.xmldoc.childNodes[0]
    self.fieldsList = analyse(self.table.attributes["fields"].value)
    self.fieldsTypeList = analyse(self.table.attributes["types"].value)
    self.id = int(self.table.attributes["id"].value)

  ## Returns a field list
  # on renvoie une liste des champs
  def fields(self,name):
    result = []
    l = self.table.getElementsByTagName(name)
    for c in l:
      a = c.firstChild.data
      result.append(a)
    return result

  ## Returns result n° number 
  # on renvoie le resultat n° number 
  def record(self,number):
    rs = self.table.getElementsByTagName("record")
    r = rs[number]
    result = {}
    for c in self.fieldsList:
      result[c] = r.getElementsByTagName(c)[0].firstChild.data
    return result
  
  def getScheme(self):
    result = {}
    for i in range(len(self.fieldsList)):
      result[self.fieldsList[i]]= self.fieldsTypeList[i]
    return result

  def getId(self):
    return self.id
  
  ## s is typed accordingly to schema[c]
  # on type s en fonction de schema[c]
  def typage(schema,c,s):
    return s

  ## Table is filled in dynamic representation
  ## First element of the list is the table scheme
  # on remplit la table en représentation dynamique
  # le premier element de la liste est le schéma de la table
  def fillTable(self):
    rs = self.table.getElementsByTagName("record")
    schema = self.getScheme()
    result = [schema]
    for record in rs:
      tmp = {}
      for c in self.fieldsList:
        liste = record.getElementsByTagName(c)[0].childNodes
        chaine = getAllChildrenContent(liste)
        chaine = DecodeReading(clean_string(chaine))
        tmp[c] = typage(schema,c,chaine)
      tmp["id"] = int(record.attributes["id"].value)
      result.append(tmp)
    return result


## Table list is transformed into xml before being saved to table file
# on récupère la liste table est on la passe en xml avant de la sauvegarder
# dans le fichier table
class xmlWriter:
  """ objet d'ecriture du fichier xml à partir de la representation dynamique de la table """
  def __init__(self,name):
    self.name = name
    self.id = 0

  def commit(self,table,info):
    ## xml saving
    # sauvegarde xml
    save = minidom.Document()
    ## List of fields contained in the first recording
    # liste des champs contenu dans le premier enregistrement
    fieldsDescriptor = table[0]
    fieldsList = fieldsDescriptor.keys()
    try:
      fieldsString = fieldsList[0]
      fieldsTypeString = fieldsDescriptor[fieldsList[0]]
    except:
      print "la table ne contient aucun champ" ## gettext
    for field in fieldsList[1:]:
      fieldsString += ("," + field)
      fieldsTypeString += ("," + fieldsDescriptor[field])
    ## Creation of table node
    # creation du noeud table
    tableNode = save.createElement("table")
    tableNode.setAttribute("fields",fieldsString)
    tableNode.setAttribute("types",fieldsTypeString)
    tableNode.setAttribute("id",str(info["id"]))
    save.appendChild(tableNode)
    ## Creation of a marker record for every recording of the table
    ## but the first element of the table which is not a record
    # on cree une balise record pour chaque enregsitrement
    # de la table, en ne tenant pas compte du premier elt
    # de la liste table qui n'est pas un record.
    for record in table[1:]:
      print "ok1"
      rc = save.createElement("record")
      id = str(self.id)
      print id
      self.id += 1
      rc.setAttribute("id",id)
      tableNode.appendChild(rc)
      ## Creation of fields markers
      ## together with the text content
      # on cree les balises de champs
      # ainsi que le texte qu'elles contiennent
      for field in fieldsList:
        c = save.createElement(str(field))
        rc.appendChild(c)
        text = save.createTextNode(EncodeToWrite(record[field]))
        c.appendChild(text)
      ## Making of a backup file of previous version
      # on fait un fichier de backup de la version précédente
      back = self.name + "_back"
    try:
      rename(self.name,back)
    except:
      print "le fichier de sauvegarde était inexistant" ## _ for gettext
    try:
      texte = save.toprettyxml()
    except:
      print "la transformation to prettyxml() n'a pas fonctionné"
    print "suite de la sauvegarde"
    save_file = open(self.name,"w")
    save_file.write(save.toprettyxml())
    save_file.close()
    return 0


