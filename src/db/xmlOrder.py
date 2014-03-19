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


## Function to sort the list accordingly to order
# fonction pour ordonner la liste selon order
def AvoidTwin(liste):
  """ this function erase all twins in an ordered list """
  l = len(liste)
  if l <= 1:
    return liste
  elif liste[0] == liste[1]:
    return AvoidTwin(liste[1:])
  else:
    return [liste[0]] + AvoidTwin(liste[1:])
    
    

def OrderedList(order,liste):
  if order == None:
    return liste
  ## else order is a pair (field name n, 0/1) 0 for desc, else 1
  # sinon order est un doublet (nom de champ n, 0/1) 0 pour desc 1 sinon
  field = order[0]
  fieldList = []
  for i in liste:
    fieldList.append(i[field])
  ## Sorting the list of wanted fields
  # on trie la liste des champs voulus
  fieldList.sort()
  print fieldList ## debug
  fl = AvoidTwin(fieldList)
  print fl
  if not order[1]:
    fl.reverse()
  result = []
  for i in fl:
    for j in liste:
      if j[field] == i:
        result.append(j)
        liste.remove(j)  
  return result
