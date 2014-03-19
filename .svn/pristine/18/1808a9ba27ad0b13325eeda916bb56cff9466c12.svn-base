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
import os, sys, tempfile, subprocess
import urllib, htmlentitydefs
import re
from lxml import etree

from modules import module_interfaces
from modules import themodule_Wiki as Wiki


from conf import confstatic
import conf_general, conf_private
from conf import utils



class TMException(Exception):
  pass

class TemplateManager:

  def __init__(self, db, page, args):
    #raise TMException("Erreur")
    self.db = db
    self.page = page
    self.args = args
    self.priorities=[]   #liste des modules à afficher, classée par ordre d'affichage
    pass


  def setup_modules(self, mm):
    """ici on a accès à la variable self.page qui contient le nom de la page
    demandée, "default" sinon. On peut alors interroger la base de données pour
    savoir quels sont les modules à activer pour cette page. On les active
    ci-dessous"""

    # the "pages" table is changed dynamically (a column is added as soon as a
    # new module appears) : that way, for every page, each module has its own
    # priority within the page. the goal of the following lines is to find the
    # biggest priority and then add the modules in the self.priorities list with
    # the order wanted

    self.mm = mm
    self.mm.page = self.page
    pages = self.db.table("pages").select(cond=[("page_id","=",self.page)])
    if len(pages) == 0:
      pages = self.db.table("pages").select(cond=[("page_id","=",confstatic.default_page_name)])
      if len(pages) == 0:
        return
    page = pages.next()
    modules = self.mm.get_available_modules()

    max_priority=-1
    self.priorities=[]
    for m in modules:
      if page.has_key(m+"_priority"):
        p = page[m+"_priority"]
        if max_priority<p:
          max_priority=p
        if p!=-1:
          self.priorities.append("")   #on remplit le tableau des priorités

    for m in modules:
      if page.has_key(m+"_priority"):
        p = page[m+"_priority"]
        if p!=-1:
          self.priorities[max_priority-p]=m   #on affecte les modules


  def generate_header(self):
    """Génère l'en-tête DocBook ainsi que le titre : ce sont les mêmes quel que
    soit le format de sortie. Réinitialise le docbook. Toujours appeler avant de
    commencer la génération !"""
    self.pagename=self.db.table(confstatic.pages_database_prefix).select(cond=[("page_id","=",self.page)]).next()

    self.doc_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    self.doc_string += "<!DOCTYPE article PUBLIC \"-//OASIS//DTD DocBook XML V4.1.2//EN\"\n"
    self.doc_string += " \"http://www.oasis-open.org/docbook/xml/4.1.2/docbookx.dtd\">\n"
    self.doc_string += "<article>\n"
    self.doc_string += "<articleinfo>\n"
    self.doc_string += "<title>"
    self.doc_string += self.pagename["page_title"] + "</title>\n"
    self.doc_string += "</articleinfo>\n"

  def generate_body(self, mode):
    """Génère le corps de la page avec des adaptations selon que mode vaut pdf
    ou xhtml"""
    for key in self.priorities:
      m = self.mm[key]
      if mode == "pdf" and self.mm[key].module_name() == confstatic.module_menu_name:
        continue
      if isinstance(m, module_interfaces.IModuleContentProvider):
        if self.mm[key].module_name() == confstatic.module_wiki_name: # the Wiki module has its own <sect1>s so don't add them ourselves
          self.doc_string += self.mm[key].generate_content_xml(self.args)
        elif not (mode == "pdf" and self.mm[key].module_name() == confstatic.module_menu_name): # the only case to avoid: being in a PDF and generating the menu
          self.doc_string += "<sect1>"
          if mode=="xhtml":
            self.doc_string += "<idComfort>"+(self.mm[key].module_id())+"</idComfort>"
          if self.mm[key].module_title()!="": # try in every case to get a title for the <sect1> we're in
            self.doc_string += "<title>"+(self.mm[key].module_title())+"</title>\n"
          elif mode == "pdf": # only use this solution if in PDF (otherwise, make a title for the menu)
            self.doc_string += "<title>"+(self.mm[key].module_name())+"</title>\n"
          self.doc_string += self.mm[key].generate_content_xml(self.args)
          self.doc_string += "</sect1>\n"

    #contenu de la page -- fin
    self.doc_string += "</article>\n"

  def do_xslt(self, mode):
    """Fait la transformation XSLT sur self.doc_string, y'a beaucoup de code en
    commun donc ça change pas. Doit être fait dans le dossier de CoMFoRT.
    @param mode: ou bien pdf, ou bien html
    @return: la chaîne résultant de la transformation"""

    if mode == "pdf":
      xsl_file = os.path.join('templates','xsl','fo','docbook.xsl')
    elif mode == "xhtml":
      xsl_file = os.path.join('templates','xsl','xhtml','docbook.xsl')

    #définition de la fonction de la transformation xslt
    xsl_doc = etree.parse(xsl_file)
    ac = etree.XSLTAccessControl(read_file=True)
    transform = etree.XSLT(xsl_doc, access_control=ac)

    if mode == "pdf":
      opts = {}
    elif mode == "xhtml":
      opts = {'html.stylesheet' : "'"+confstatic.get_style_url(self.pagename["page_style"])+"'",
          'generate.toc' : "'article nop'"}
    try:
      doc_tree  = etree.fromstring(self.doc_string)
    except etree.XMLSyntaxError, e:
      utils.error_page("""
Erreur erreur ! Un module a généré du mauvais DocBook. Le DocBook était le
suivant, merci de nous envoyer un rapport de bug assorti du DocBook ci-dessous
et de l'exception.

Exception:
%s

DocBook
%s
  """ % (e, utils.htmlentities(self.doc_string.decode("utf-8")).encode("latin1")))
      sys.exit(0)
    tree = transform(doc_tree, **opts)
    string = etree.tostring(tree, pretty_print=True)

    return string
    

  def generate_pdf(self, redir=True):
    """Génération format PDF."""
    utils.mkdirp(confstatic.generate_path)

    self.generate_header()
    self.generate_body("pdf")

    if conf_general.pdfmode == "fop":
      fo_string = self.do_xslt("pdf")

      (fd, fname) = tempfile.mkstemp(suffix=".xml", text=True)
      f = os.fdopen(fd, "w")
      f.write(fo_string)
      f.close()

      args2 = self.args.copy()
      args2["pdf"] = "1"

      p = subprocess.Popen([confstatic.fop_path, "-fo", fname, "-pdf",
        os.path.join(confstatic.generate_path, confstatic.build_url(args2))],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      r = p.wait()
      if r:
        utils.error_page(_("""Impossible de lancer FOP. Code de retour d'erreur : %d.
Voici la sortie standard :
%s
Voici la sortie d'erreur :
%s

Le fichier xml %s a été gardé (à joindre à tout rapport de bug)
""" % (r, p.stdout.read(), p.stderr.read(), fname)))
      if not r:
        os.remove(fname)

    elif conf_general.pdfmode == "latex":
      (fd, fname) = tempfile.mkstemp(suffix=".xml", text=True)
      f = os.fdopen(fd, "w")
      f.write(self.doc_string)
      f.close()

      args2 = self.args.copy()
      args2["pdf"] = "1"

      if os.name == "nt":
        dblpath = confstatic.nt_python_path+"python.exe"
      else:
        dblpath = confstatic.dblatex_path()
      p = subprocess.Popen([dblpath, "--pdf", "-s", "db2latex", "-o",
        os.path.join(confstatic.generate_path, confstatic.build_url(args2)),
        fname],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      r = p.wait()
      if r:
        utils.error_page(_("""Erreur au lancement de DBLatex. Les raisons possibles sont :
  - utilisation d'un GIF animé (déconseillé) ;
  - oubli d'un sous-titre.
  - mauvais droits (supprimez /tmp/comfortlog (ou
    c:\\Windows\\TEMP\\comfortlog), rechargez la page, et regardez le contenu du
    fichier
Si vous ne pouvez pas faire autrement, utilisez FOP (à changer dans la configuration).
Code de retour d'erreur : %d.
Sortie standard :
%s
Sortie d'erreur :
%s

Le fichier XML cité ci-dessus a été conservé, donnez-le nous pour tout rapport
de bug""" % (r, p.stdout.read(), p.stderr.read())))

      if not r:
        os.remove(fname)

    if redir and not r:
      utils.redir("%s/%s" % (confstatic.generate_url,confstatic.build_url(args2)))

    
  def generate_xhtml(self):
    """Génération XHTML"""
    self.generate_header()
    self.generate_body("xhtml")
    xhtml_string = self.do_xslt("xhtml")

    # petit hack dégueulasse : on vire les id ajoutés par lxml qui servent à rien
    # et changent trop souvent même quand on n'a rien changé dans la page
    # et donc pourraient générer des conflits qui n'existent pas
    exp = re.compile(' id="id[0-9]{7}"')
    xhtml_string = exp.sub('', xhtml_string)

    i = xhtml_string.index("<div class=\"titlepage\"") #le premier
    xhtml_string = xhtml_string[:i+22] +  " id=\"ie6hack\">" + "<div class=\"sitename\">" + utils.htmlentities(conf_general.title.decode("utf-8")) + "</div>" + xhtml_string[i+23:]

    i = xhtml_string.index("</head>")
    fav = confstatic.get_favicon_url()
    xhtml_string = xhtml_string[:i] +  """
    <link rel="shortcut icon" href="%s" type="image/x-icon" />
    <link rel="icon" href="%s" type="image/x-icon" />
    <script type="text/javascript">
sfHover = function() {
  var sfEls = document.getElementById("Menu").getElementsByTagName("LI");
  for (var i=0; i<sfEls.length; i++) {
    sfEls[i].onmouseover=function() {
      //this.className+=" sfhover";
      this.className = "sfhover";
    }
    sfEls[i].onmouseout=function() {
      //this.className=this.className.replace(new RegExp(" sfhover\\b"), "");
      this.className = "";
    }
  }
}
if (window.attachEvent) window.attachEvent("onload", sfHover);

    </script>""" % (fav,fav) + xhtml_string[i:]

    args2 = self.args.copy()
    args2["pdf"] = "1"
    args2["page"] = self.page+".html"
#
#    if utils.pdf_ok():
#      urlpdf = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href=\""+confstatic.build_url(args2)+"\">"+_("Version PDF")+"</a>"
#    else:
#      urlpdf = ""
#
#    i = xhtml_string.index("</body>")
#    l1 = """<a href="http://graal.ens-lyon.fr/comfort/">
#      <img src="../styles/comfort_thumb.png" style="border-width: 0; margin-top: -31px;" />
#      &nbsp;Powered by CoMFoRT !</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp """
#    if confstatic.generating:
#      l2 = ""
#    else:
#      l2 = """
#        <a href="admin.py?id=modpage&page_id=%s">%s</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp
#        <a href="admin.py">%s</a>
#        """ % (urllib.quote(self.page), _("Modifier cette page"), _("Panneau d'administration")) 
#
#    xhtml_string = xhtml_string[:i] + """
#    <div class=\"feet\">
#      %s
#      %s
#      %s
#    </div>
#    """ % (l1, l2, urlpdf) + xhtml_string[i:]
    
    count=0
    if utils.pdf_ok():
      count+=1
    if confstatic.generating:
      count+=1
    else:
      count+=2 
    width=100/count       
      
    if utils.pdf_ok():
      urlpdf = """<div style=\"width:%d%%; float: left; text-align: center;\"><a href=\"%s\">%s</a></div>"""%(width,confstatic.build_url(args2),_("Version PDF"))
    else:
      urlpdf = ""

    i = xhtml_string.index("</body>")
    
    if confstatic.generating:
      logo = """
      <div class="comfort">
        <a href="http://graal.ens-lyon.fr/comfort/">
          <img src="styles/comfort_thumb.png" style="border-width: 0;" alt="logo de CoMFoRT"/>
          <br />CoMFoRT
        </a>
      </div>"""
      link = """
      <div style=\"text-align: center; width=%d%%; float: left;\">
      <a href=\"http://graal.ens-lyon.fr/comfort/\">Powered by CoMFoRT !</a>
      </div>"""%(width)
    else:
      logo = """
      <div class="comfort">
        <a href="http://graal.ens-lyon.fr/comfort/">
          <img src="../styles/comfort_thumb.png" style="border-width: 0;" alt="logo CoMFoRT"/><br />
          Powered by CoMFoRT !
        </a>
      </div>"""
      link = """
      <div style=\"float: left; text-align:center; width:%d%%;\"><a href="admin.py?id=modpage&amp;page_id=%s">%s</a></div>
      <div style=\"float: left; text-align:center; width:%d%%;\"><a href="admin.py">%s</a></div>
        """ %(width, urllib.quote(self.page), _("Modifier cette page"), width, _("Panneau d'administration")) 

    if not conf_general.display_logo:
      logo = ""

    xhtml_string = xhtml_string[:i] + """
    %s
    <div class="feet">
      %s
      %s
      <div class="spacer">&nbsp;</div>
    </div>
    """ % (logo, link, urlpdf) + xhtml_string[i:]
    return xhtml_string


  def generate_wiki_xhtml(self,wiki_string):
    """Génération XHTML"""
    self.generate_header()
    
    parser=Wiki.Parser(self.db,wiki_string)
    parser.parse_wiki(page_id=self.page)
    self.doc_string += parser.generate()

#  Pour le & ? essai n°2
#    self.doc_string += parser.generate().replace("&","&amp;").replace("&amp;lt", "&lt").replace("&amp;gt", "&gt").replace("&amp;quot","&quot")
    #contenu de la page -- fin
    self.doc_string += "</article>\n"

    xhtml_string = self.do_xslt("xhtml")

    # petit hack dégueulasse : on vire les id ajoutés par lxml qui servent à rien
    # et changent trop souvent même quand on n'a rien changé dans la page
    # et donc pourraient générer des conflits qui n'existent pas
    exp = re.compile(' id="id[0-9]{7}"')
    xhtml_string = exp.sub('', xhtml_string)
    
    i = xhtml_string.index("<hr />")
    xhtml_string=xhtml_string[i:]
    
    i = xhtml_string.index("</div>")
    xhtml_string=xhtml_string[i+6:]   
    xhtml_string="<div>"+xhtml_string
    
    i = xhtml_string.index("</body>")
    xhtml_string=xhtml_string[:i]    
    
    return xhtml_string
