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

## Conditions are a list of tuples (field, type, value)
## with type being "=", "<>", "<", "<=", ">=" or ">"
# Les conditions sont une liste de tuples (champ, type, valeur)
# avec type étant "=", "<>", "<", "<=", ">=" ou ">"

## Sorts are a list made of tuples (field, bool), the boolean value tells
## wether it is an ascending (true) sort or a descending (false) sort
# les tris sont une liste de tuples (champ, bool) avec le booléen
# disant si le tri est ascendant (true) ou descendant (false)

## pysqlite import and removal of drop table
# import de pysqlite et remove pour drop table
try:
  from sqlite3 import dbapi2 as sqlite
except:
  from pysqlite2 import dbapi2 as sqlite

import os
from os import remove
from db_interface import *
from conf import confstatic

## Definition of out of class functions
# definition de fonction hors classe
def makeCond(cond):
  """function which transforms a condition list into sql condition string """
  # Emptyness of condition is tested
  # on teste si la condition est vide
  if cond == None or cond == []:
    return ""
  result = "WHERE %s %s '%s' " % (cond[0][0], cond[0][1], str(cond[0][2]))
  for a in cond[1:]:
    result += "AND %s %s %s " % (a[0], a[1], str(a[2]))
  return result

def makeOrder(order):
  """ function which transform an order into sql order string """
  if order == None:
    return ""
  else:
    s="ORDER BY "
    first=True
    for o in order:
      if not first:
        s=s+", "
        first=False
      if o[1]:
        s=s+("%s ASC" % o[0])
      else:
        s=s+("%s DESC" % o[0])
    return s



class SQL_RecordSet(IDBRecordSet):    
  def __init__(self,fetchall,fieldsList):
    """ initialize the object with fetchall() sql object """
    self.fetch = fetchall
    ## The following list describes the fields order
    # la liste suivante contient l'ordre des champs
    self.descriptor = fieldsList

  def __len__(self):
    return len(self.fetch)

  def __iter__(self):
    """ iterator of the IDBRecordSet object """    
    return self

  def next(self):
    """ next operator """
    if self.fetch == []:
      raise StopIteration
    fetchR = self.fetch[0]
    result = {}
    self.fetch = self.fetch[1:]
    for c in range(len(self.descriptor)):
      if isinstance(fetchR[c], basestring ):
        uu = unicode(fetchR[c])
        result[self.descriptor[c]] = uu.encode("utf-8")
      else:
        result[self.descriptor[c]] = fetchR[c]
    return result




class SQL_DB(IDB):

  def __init__(self, options = None):
    """ Initialise la base de données à partir d'un dictionnaire d'options """
    self.connect()


  def connect(self):
    """ Ouvre la connection à la base de données """
    self.connexion = sqlite.connect(confstatic.database_path)
    cursor = self.connexion.cursor()
    request = "SELECT * FROM STRUCTURE"
    try:
      cursor.execute(request)
    except:
      request_structure = "create table STRUCTURE (name varchar, fields varchar, type varchar) "
      cursor.execute(request_structure)
    cursor.close()
  
  
  def close(self):
    """ Ferme la connection à la base de données """
    self.connexion.close()

  
  def create(self, table, schema):
    """ create the gadfly table, all fields are text : this need a typing function for select operation"""
    cursor = self.connexion.cursor()
    requete = "CREATE TABLE %s " % (table)
    requete += "( id integer "
    for c in schema.keys():
      requete += " , %s %s " %(c,schema[c])
    requete += ")"
    cursor.execute(requete)
    for c in schema.keys():
      request = "INSERT INTO STRUCTURE (name, fields, type) VALUES ('%s', '%s', '%s')" % (table, c,schema[c])
      cursor.execute(request)
    ## Linking process is finished
    ## Commitment and closing of the connection
    # les operations de connexion sont terminees
    # commit puis fermeture de la connexion
    self.connexion.commit()
    cursor.close()
         
  def table(self, name):
    """open the named table"""
    return SQL_Table(self,name)

  def drop(self, table):
    """ delete the table called table """
    cursor = self.connexion.cursor()
    request = "DROP TABLE %s " % table
    cursor.execute(request)
    condString = makeCond([("name","=",table)])
    request = "DELETE FROM STRUCTURE %s" %  condString
    cursor.execute(request)
    cursor.close()


  def __del__(self):
    self.close()



class SQL_Table(IDBTable): 
  def __init__(self, db, table):
    """init of the object table """
    ## Tests if the table is struck
    # teste si la table est bloque
    self.db = db
    self.table = table

    ## Table scheme will be taken off
    # on va retirer le schema de la table
    cursor = self.db.connexion.cursor()
    request = "SELECT fields,type FROM STRUCTURE WHERE name='"+self.table+"'"
    cursor.execute(request)
    self.schema = {}
    for i in cursor.fetchall():
      self.schema[i[0]] = i[1]
    self.SetId()
    cursor.close()

  def SetId(self):
    ## Looking for the total number of records
    # on cherche le nombre total de record
    cursor = self.db.connexion.cursor()
    request = "SELECT id FROM %s ORDER BY id" % self.table
    cursor.execute(request)
    self.current_id = -1
    self.number = 0
    for i in cursor.fetchall():
      if i[0]>self.current_id:
        self.current_id = i[0]
      self.number += 1
    ## Icrements last id found if no
    ## record is found in the table
    # on incremente de 1 la dernier id trouvee
    # s'il n'y a aucun enregistrement dans la table
    self.current_id += 1
    cursor.close()
           
  def GetScheme(self):
    """ return the table scheme, under the form of a dictionnary : fields -> type """
    return self.schema
    
  def insert(self, record):
    """ insert of a new record in the table """
    requete = "INSERT INTO %s (id " % self.table
    values = "values ( ? "
    valuesTuple = (self.current_id,)
    self.current_id += 1
    for i in record.keys():
      requete += ", %s " % i
      values += ", ? " 
      valuesTuple += (record[i],)
    requete = requete + ")" + values + ")"
    cursor = self.db.connexion.cursor()
    cursor.execute(requete,valuesTuple)
    cursor.close()
    return cursor.lastrowid
    
  def select(self, order = None, cond = None, limit = None, offset = None):
    """ outil de selection """
    condString = makeCond(cond)
    condOrder = makeOrder(order)
    fieldsString = "id"
    fieldsList = ["id"]
    ## Fields list is defined so that they appear in a known order
    # on fait la liste des champs pour qu'ils apparaissent dans un ordre connu
    for i in self.schema.keys():
      fieldsList.append(i)
      fieldsString += ", %s " % i     
    requete = "SELECT %s FROM %s " % (fieldsString, self.table)
    requete += condString
    requete += condOrder
    cursor = self.db.connexion.cursor()
    cursor.execute(requete)
    recordset=SQL_RecordSet(cursor.fetchall(), fieldsList)
    cursor.close()
    return recordset

  def update(self, record, cond = None):
    """ update function of the table, it needs a whole record : maybe use select before """       
    condString = makeCond(cond)
    request = "UPDATE %s SET " % self.table
    if len(record) != 0:
      a = record.keys()[0]
      request += " %s = ?" % (a)
      values = (record[a],)
      for c in (record.keys())[1:]:
        request += ", %s = ? " % (c)
        values += (record[c],)
    request += condString
    cursor = self.db.connexion.cursor()
    cursor.execute(request,values)
    cursor.close()
    return 1


      
  def delete(self, cond = None):
    """ delete function, delete all table's record verifying cond """        
    condString = makeCond(cond)
    request = "DELETE FROM %s %s " % (self.table, condString)
    cursor = self.db.connexion.cursor()
    cursor.execute(request)
    cursor.close()



  def commit(self):
    """ save the change into save file """
    self.db.connexion.commit()
    return 1


  def rollback(self):
    """ return to old db version, forgetting all recents modifications """
    self.db.close()
    self.db.connect()
    self.SetId()


 
     
  def begin_transaction(self):
    """ lock the table, to avoid fork and merge problem """
    request = "LOCK TABLE %s IN ACCESS EXCLUSIVE MODE" % (self.table)
    cursor = self.db.connexion.cursor()
    cursor.execute(request)
    cursor.close()
    

    
  def end_transaction(self):
    """ unlock the table """
    request = "LOCK TABLE %s IN ACCESS SHARE MODE" % (self.table)
    cursor = self.db.connexion.cursor()
    cursor.execute(request)
    cursor.close()
   
  def __del__(self):
    """ close fonction, it commits the table and ends """
    self.commit()

      


def new_db(options=None):
  """ Ouvre la base de données """
  return SQL_DB(options)
