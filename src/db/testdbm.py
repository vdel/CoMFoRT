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
from db_manager import *
a = DBManager(0)
a.create("essai",{"date" : "text", "heure": "text"})
t = a.table("essai")
if t.begin_transaction():
  print "table ouverte correctement"
else:
  "echec a l'ouverture de la table"
t.insert({"date" : "today", "heure" : "h" })
t.insert({"date" : "today", "heure" : "he" })
t.insert({"date" : "tody", "heure" : "hr" })
for c in t.select():
  print c
for c in t.select([("date","=","today")]):
  print c
t.update({"heure" : "hour"},[("date","=","today")])
for c in t.select():
  print c
t.end_transaction()
a.drop("essai")
a.create("od", {"date" : "text", "heure" :"text"} )
t = a.table("od")
if t.begin_transaction():
  print "od correctement ouverte"
else:
  print "echec a l'ouverture de od"
t.insert({"date" : "today", "heure" : "h" })
t.insert({"date" : "today", "heure" : "he" })
t.insert({"date" : "tody", "heure" : "chr" })
t.insert({"date" : "today", "heure" : "ah" })
t.insert({"date" : "today", "heure" : "bhe" })
t.insert({"date" : "tody", "heure" : "he" })
for c in t.select():
  print c
for c in t.select(None,[("heure","=","he")]):
  print c
for c in t.select(("heure",1)):
  print c
#t.end_transaction()
#a.drop("od")
