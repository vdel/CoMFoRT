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
## wether it is an ascending sort or a descending sort
# les tris sont une liste de tuples (champ, bool) avec le booléen
# disant si le tri est ascendant ou descendant

class ImplementationError(Exception):
    pass

class IDBRecordSet:
    
    def __iter__(self):
        return self

    def next(self):
        """ Retourne un dictionnaire """        
        raise ImplementationError
        

class IDB:

  def __init__(self, options):
	  ## Init the data base from a dictionary of options
    # Initialise la base de données à partir d'un dictionnaire d'options 
    raise ImplementationError
    
  def create(self, table, schema):
    ## Create the table called 'table' with the dictionnary 'schema' which associates the names of fields to the following types `id', `int', `date', ou `text' """
    # Crée la table `table' avec le dictionnaire `schema' qui associe aux noms de champs les types suivants : `id', `int', `date', ou `text' """
    raise ImplementationError
        
  def drop(self, table):
    ## Erase the table called 'table'
    # Efface la table `table' """
    raise ImplementationError

  def table(self,table):
    ## open the table called 'table'
    # open table 'table' """
    raise ImplementationError

        
class IDBTable:
    
    def __init__(self, db, name):
        ## Load the table called 'name' in the data base 'db'
        # Charge la table `name' de la base de données `db' """
        raise ImplementationError

    def schema(self):
        ## Return a dictionary describing the sheme of the table
        # Retourne un dictionnaire décrivant le schéma de la table     
        raise ImplementationError
    
    
    def insert(self, record):
        ## Insert the dictionary 'record' as a field in the table and return its id
        # Insère le dictionnaire `record' comme champ dans la table et retourne éventuellement son id """
        raise ImplementationError
    
    def select(self, order = None, cond = None, limit = None, offset = None):
        ## Look for records of the table which check the conditions defined by 'cond', and sort the records with 'order'
        # Recherche les enregistrements de la table qui satisfont la combinaison de conditions décrite par `cond',  
        # triés par les ordres décrits par `order', en limitant éventuellement les résultats.
        # Retourne un IDBRecordSet
        raise ImplementationError

    def update(self, record, cond = None):
        ## Update the table with the dictionary 'record' for all records that check the conditions defined by 'cond'
        # Met à jour la table avec le dictionnaire `record' pour les enregistrements qui satisfont la combinaison de
        # conditions décrite par `cond'     
        raise ImplementationError
        
    def delete(self, cond = None):
        ## Erase the records of the table which check the conditions defined by 'cond'
        # Efface les enregistrements de la table qui satisfont la combinaison de conditions décrite par `cond'
        raise ImplementationError
        
    def commit(self):
        ## Save all modifications
        # Sauve les modifications effectuées 
        raise ImplementationError
        
    def rollback(self):
        ## Reload the table ignoring modifications which are not saved
        # Recharge la table en ignorant les modifications non sauvegardées 
        raise ImplementationError

    def begin_transaction(self):
        ## Lock the table
        # Verrouille la table 
        raise ImplementationError

    def end_transaction(self):
        ## Unlock table
        # Dévérouille la table 
        raise ImplementationError

    def __del__(self):
        ## End the current transaction and commit
        # Finit la transaction en cours et commite 
        raise ImplementationError
