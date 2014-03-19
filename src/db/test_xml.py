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
from db_xml import *

a = new_db(42)
d = { "date" : "text" , "heure" : "text" } 
a.create("essai",d)
table = a.table("essai")
print "id de table vaut %d " % (table.id)
r = { "date" : "hier", "heure" : "aucune" } 
r2 = { "date" : "hier2", "heure" : "2aucune" } 
print table.insert(r)
print table.insert(r)
print table.insert(r2)
cond1 = ("date","=","hier")
d2 = {"date" : "today", "heure" : "aucune"}
print table.insert(d2)
print "selection 1"
c1 = table.select(None,[cond1])
for h in c1:
  print h
c2 = table.select()
print "selection 2 : total"
for h in c2:
  print h
d3 = { "date" : "aujourdhui"}
table.update(d3,[cond1])
c3 = table.select()
print "selection 3"
for h in c3:
  print h
print "selection 3 bis"
for h in table.select(None,[("date","=","today")]):
  print h
table.delete([("date","=","today")])
print "selection apres suppression"
for h in table.select():
  print h
print "schema"
print table.GetScheme()
print "selection 4"
table.commit()

