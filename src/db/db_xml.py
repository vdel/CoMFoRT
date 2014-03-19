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

from db_interface import *
from db_condition import *
from parser_minidom import xmlWriter, xmlReader

## Import of lock functions
# import des fonctions lock
from xmlLock import *
## Import of functions that manage selects order
# import des fonctions pour gérer l'ordre des selects
from xmlOrder import OrderedList

## conf variables
#variables de conf
LockEnable = 0

# fonction de copie en profondeur d'un dictionnaire
# pour éviter des erreurs lors de l'ajout d"un même dico
def DicCopy(dic):
  a = {}
  for c in dic.keys():
    a[c] = dic[c]
  return a

class DBXMLRecordSet(IDBRecordSet):
  def __init__(self,liste):    
    self.liste = liste
    self.index = 0

  def __iter__(self):
    return self
  
  def next(self):
    if self.index >= len(self.liste):
      raise StopIteration
    else:
      self.index += 1 
      return self.liste[self.index - 1]

  def __len__(self):
    return len(self.liste)
    


class DBXML(IDB):    # on surdéfini IDB
  def __init__(self, options):
    """ init function, any action is defined """
    self.verrou = []
    self.CurrentSessionId = 0 ## session allocation id (object)
                              # id d'allocation de session (objet)
    self.options = options

  def create(self, table, schema):
    """ create the table called table with the given schema : opens a xml file
      and loads scheme into it """
    ## Creating file for saving the table
    # on crée le fichier de sauvegarde de la table
    f = open(table, "w")
    f.close()
    ## Creating the pattern of the table
    # on crée le motif de la table
    tableStruct = [schema]
    ## The object is saved
    # on appelle l'objet se sauvegarde
    save = xmlWriter(table)
    info = {}
    info["id"] = 0
    save.commit(tableStruct,info)
        
  def drop(self, table):
    """ drop the given table : deleting table file"""
    remove(table)

  def table(self,table):
    """ function to open given table and load it into memory """
    tmp = self.CurrentSessionId
    self.CurrentSessionId += 1
    return DBXMLTable(self,table,tmp)



            
class DBXMLTable(IDBTable): # on surdéfini IDBTable dans XMLDBTable
    
  """ Charge la table `name' de la base de données `db' """
  def __init__(self,db, name,id):
    docxml = xmlReader(name)
    self.table = docxml.fillTable()
    self.schema = docxml.getScheme()
    self.id = docxml.getId()
    self.name = name
    self.db = db
    self.SessionId = id ## identifier used by db for the locks
                        # identificateur utilisé par db pour les verrous

  def ExclusionTest(self):
    """   before each operation, test if this object is able to
      do that op, satisfying db lock """
    if not LOCKENABLE:
      return 1 ## Locks are out of order, nothing to do
               # les verrous sont hors service, rien à faire
    else:
               ##TODO how many ?
               # TODO retourner combien nico???
      return 0
      

 
  def GetScheme(self):
    """ return a descriptive dictionnary of the table """
    return self.schema
    
  def insert(self, record):
    """ insert the given record in the table, returning the id"""
    tmpId = self.id
    record["id"] = tmpId
    tmpRecord = DicCopy(record)
    self.table.append(tmpRecord)
    self.id += 1
    return (record["id"])
        
    
  def select(self, order = None, cond = None, limit = None, offset = None):
    """ search for records in the table that makes true the whole cond lists """
    liste = []
    ## case in which there are no conditions
    # cas où on n'a pas de condition
    if cond == None:
      liste = self.table[1:]
      return liste.__iter__()
    for i in range(len(self.table))[1:]:
      if verifie_conditions(cond,self.table[i]):
          liste.append(self.table[i])
    ## List needs now to be sorted according to this order
    # il faut maintenant trier la liste selon ordre
    liste = OrderedList(order,liste) 
    return DBXMLRecordSet(liste)    
    

  def update(self, record, cond = None):
    """ update the table with record dico of all record that agree cond lists """ 
    #for rec in self.table[1:]:
    for i in range(1,len(self.table[1:])):
      rec  = self.table[i]
      if verifie_conditions(cond,rec):
          for c in record.keys():     # erreur sur update, opn ne change que les champs demandés, on ne refait pas un record
            self.table[i][c] = record[c]
        
  def delete(self, cond = None):
    """ delete all records in table that satisfy cond list"""
    i = 1
    while i != len(self.table):
      if verifie_conditions(cond,self.table[i]):
        self.table.remove(self.table[i])
      else:
        i = i + 1
        
  def commit(self):
    """ commit this table, saving change into xml files """
    #f = open(self.name, "w")
    #f.close()
    ## Creation of table pattern
    ## The object is saved
    # on crée le motif de la table
    # on appelle l'objet se sauvegarde
    save = xmlWriter(self.name)
    info = {}
    info["id"] = self.id
    save.commit(self.table,info)
        
  def rollback(self):
    """ discard all recent changes, back to previous table version (still in xml file) """
    docxml = xmlReader(self.name)
    self.table = docxml.fillTable()
    self.schema = docxml.getScheme()
    self.id = docxml.getId()


  def begin_transaction(self):
    """ lock table transaction, unused in xml implement """
    raise ImplementationError

  def end_transaction(self):
    """ unlock table transaction, unused in xml implement """
    raise ImplementationError

  def __del__(self):
    """ close function of XML base, commit changes and quit """
    self.commit()
    

def new_db(options=None):
  """ ouvre la base de donnée """
  return DBXML(options)
