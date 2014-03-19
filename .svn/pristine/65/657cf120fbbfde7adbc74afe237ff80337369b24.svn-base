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

## Database keeps in memory a dictionnary, the
## keys are names of tables, values and session
## identifier of the object that locks currently
## the table. If the key does not exist or if its
## value is associated to None, then table is not
## locked, else it is locked by the corresponding id
# la db maintient en mémoire une dictionnaire
# les clef sont les noms des tables et les valeurs
# l'identificateur de session de l'objet qui vérouille
# actuellement la table, si la clé n'existe pas ou si
# la valeur associée est à None alors la table n'est 
# pas vérouillée, sinon elle l'est pas l'id correspondante

def TestLock(LockList,table,id):
  """ tests if given table is correctly locked or is able to be locked
    by current object """
  if table in LockList.keys():
    ## Session is allowed to relock the table if needed
    # on permet à une session de rebloquer la table si nécessaire
    if LockList[table] == id or LockList[table] == None:
      return 1
    else:
      return 0
  else:
    return 1 ## table has not been locked yet
             # la table n'a pas encore été vérrouillée

def StrongTestLock(tableObject):
  """ test if given table had been rightly locked by object before operation """
  db = tableObject.db
  table = tableObject.name
  if db.verrou[table] == table.sessionId:
    return 1
  else:
    return 0

def LockTable(db,table,id):
  """ If possible locks given table, returns 0 else """
  if TestLock(db.verrou,table,id):
    db.verrou[table] = id
    return 1
  else:
    return 0

def UnlockTable(db,table,id):
  """ if right unlock given table, returns 0 else"""
  if TestLock(db.verrou,table,id):
    if db.verrou[table] != id:
      print "current object does not lock table before unlock" #gettext
    db.verrou[table] = id
    return 1
  else:
    print "impossible to unlock given table ( object/table lock do not match " #gettext
    return 0
