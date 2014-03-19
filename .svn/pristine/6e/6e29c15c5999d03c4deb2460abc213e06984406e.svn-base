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
from lxml import etree

doc_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
doc_string += "<!DOCTYPE article PUBLIC \"-//OASIS//DTD DocBook XML V4.1.2//EN\"\n"
doc_string += " \"http://www.oasis-open.org/docbook/xml/4.1.2/docbookx.dtd\">\n"
doc_string += "<article>\n"
doc_string += "<articleinfo>\n"
doc_string += "<title>CoMFoRT - "
doc_string += " hehe !</title>\n"
doc_string += "</articleinfo>\n"
#contenu de la page -- debut
doc_string += "<sect1>\n"
doc_string += "</sect1>\n"
doc_string += "<sect1>\n"
doc_string += "</sect1>\n"
#contenu de la page -- fin
doc_string += "</article>\n"

#definition de la fonction de la transformation xslt
xsl_doc = etree.parse('xsl/xhtml/docbook.xsl')
ac = etree.XSLTAccessControl(read_file=True)
transform = etree.XSLT(xsl_doc, access_control=ac)

# on transforme le docbook brut au format string en du xhtml au
# format string en passant par les types internes de etree pour
# faire la transformation xslt :
# doc_string -> doc_tree -> xhtml_tree -> xhtml_string
doc_tree  = etree.fromstring(doc_string)
xhtml_tree = transform(doc_tree)
xhtml_string = etree.tostring(xhtml_tree)
xhtml_string_indented = etree.tostring(xhtml_tree, pretty_print=True)


#version moche
#print xhtml_string

#version jolie (indentation)
#print xhtml_string_indented



TEST_doc_tree = etree.parse('test.xml')
TEST_xhtml_tree = transform(TEST_doc_tree)
TEST_xhtml_string_indented = etree.tostring(TEST_xhtml_tree, pretty_print=True)
print TEST_xhtml_string_indented
