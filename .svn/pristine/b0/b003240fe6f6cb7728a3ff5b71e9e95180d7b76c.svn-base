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


from conf import confstatic
import conf_general, conf_private

import ftplib
import os
import sys
import time
import pickle
try:
  import hashlib
except ImportError:
  import md5 as hashlib

import generate


class SyncError(Exception):
  """
  Classe d'exception utilisée pour signaler tout problème de synchronisation
  """
  def __init__(self, str, conflict=False):
    self.str = str
    self.conflict = conflict

  def is_conflict(self):
    """
    Indique si l'erreur est un conflit entre la version locale et la version en ligne.
    @return: True si conflit, False sinon
    """
    return self.conflict

  def get_error(self):
    """
    Donne des détails sur l'erreur.
    @return: chaine de caractère décrivant l'erreur survenue
    """
    return self.str


class _transferer:
  def _createLocalDirFor(self, f):
    """
    Crée si nécessaire le dossier local pour le fichier f de la session distante.
    @type f: string
    @param f: chemin d'un fichier
    """
    dir = os.path.dirname(f)
    if dir and dir != '.':
      if not os.path.isdir(dir):
        try:
          self._createLocalDirFor(dir)  # on crée les sous répertoires ## Sub-directories are created
          os.mkdir(dir)
        except:
          raise SyncError(_("Le dossier local '%s' n'existe pas et impossible de le créer." % dir))

  def quit(self):
    """
    Ne fait rien par défaut.
    """
    pass


class _transferer_FTP(_transferer):
  """
  Classe assurant le transfert de fichiers sur le serveur distant par FTP.
  """
  def __init__(self):
    """
    Établit la connection FTP (et lève une SyncError si un problème surgit).
    """
    try:
      self.session_ftp = ftplib.FTP(conf_private.server_ftp, conf_private.user_ftp, conf_private.pass_ftp)
    except:
      raise SyncError(_("Impossible de se connecter au serveur FTP."))
#    self.session_ftp.set_debuglevel(2)  # mettre 1 ou 2 pour avoir des messages de debugages affichés sur stdout
                                         ## set to 1 or 2 to get debug messages on stdout
    if conf_private.root_ftp[-1:] != '/':
      root_dir = conf_private.root_ftp + "/"
    else:
      root_dir = conf_private.root_ftp
    try:
      self._createDirFor(root_dir)
    except:
      self.session_ftp.quit()
      raise SyncError(_("Le dossier racine du site '%s' n'existe pas et impossible de le créer.") % conf_private.root_ftp)
    self.session_ftp.cwd(root_dir)

  def _createDirFor(self, f):
    """
    Crée si nécessaire le dossier pour le fichier f sur la session FTP.
    @type f: string
    @param f: chemin d'un fichier
    """
    dir = os.path.dirname(f)
    sys.stdout.flush()
    if dir and dir != '.':
      try:
        # vérification de l'existence du dossier.
        ## check the directory's existence.
        pathname = self.session_ftp.pwd()
        self.session_ftp.cwd(dir)
        self.session_ftp.cwd(pathname)
      except:
        try:
          self._createDirFor(dir)  # on crée les sous répertoires ## subedirectories are created
          self.session_ftp.mkd(dir)
        except:
          raise SyncError(_("Le dossier '%s' n'existe pas et impossible de le créer." % dir))
    
  def sendFile(self, f):
    """
    Envoie le fichier f sur la session FTP.
    Affiche une ligne indiquant l'envoi sur la sortie standard.
    @type f: string
    @param f: fichier à envoyer
    """
    print "<li>"+(_("Envoi du fichier '%s'") % f)+"</li>"
    sys.stdout.flush()
    self._createDirFor(f)
    try:
      fd = open(f)
      if f.endswith('.html'):
        self.session_ftp.storlines(('STOR %s' % f), fd)
      else:
        self.session_ftp.storbinary(('STOR %s' % f), fd)
      fd.close()
    except:
      raise SyncError(_("Impossible d'envoyer le fichier '%s'." % f))

  def retFile(self, f):
    """
    Récupère le fichier f sur la session FTP.
    Affiche une ligne indiquant la reception sur la sortie standard.
    @type f: string
    @param f: fichier à récupérer
    """
    print "<li>"+(_("Récupération du fichier '%s'") % f)+"</li>"
    sys.stdout.flush()
    self._createLocalDirFor(f)
    try:
      fd = open(f, 'w')
      if f.endswith('.html'):
        self.session_ftp.retrlines('RETR %s' % f, fd.write)
      else:
        self.session_ftp.retrbinary('RETR %s' % f, fd.write)
      fd.close()
    except:
      raise SyncError(_("Impossible de récupérer le fichier '%s'." % f))

  def quit(self):
    """
    Ferme la connection.
    """
    self.session_ftp.quit()


class _transferer_SSH(_transferer):
  """
  Classe assurant le transfert de fichiers sur le serveur distant par SSH.
  """
  def sendFile(self, f):
    """
    Envoie le fichier f.
    Affiche une ligne indiquant l'envoi sur la sortie standard.
    @type f: string
    @param f: fichier à envoyer
    """
    print "<li>"+(_("Envoi du fichier '%s'<br />") % f)+"</li>"
    sys.stdout.flush()
    try:
      os.system('%s %s %s/%s' % (confstatic.scp_path(), f, conf_private.server_ssh, f))
    except:
      raise SyncError(_("Impossible d'envoyer le fichier '%s'." % f))

  def retFile(self, f):
    """
    Récupère le fichier f.
    Affiche une ligne indiquant la reception sur la sortie standard.
    @type f: string
    @param f: fichier à récupérer
    """
    print "<li>"+(_("Récupération du fichier '%s'<br />") % f)+"</li>"
    sys.stdout.flush()
    try:
      os.system('%s %s/%s %s' % (confstatic.scp_path(), conf_private.server_ssh, f, f))
    except:
      raise SyncError(_("Impossible de récupérer le fichier '%s'." % f))


class _finder:
  """
  Classe offrant des outils pour permettre de déterminer quels fichiers
  ont besoin d'être uploadés ou non par FTP.
  """
  def __init__(self, trans):
    """
    @type trans: _transferer
    @param trans: objet _transferer permettant d'envoyer et récupérer les informations sur les fichiers se trouvant sur le serveur
    """
    self.conflict = False
    self.mt_file = '.mtimes'
    self.trans = trans
    try:
      fd = open(self.mt_file)
      self.last_local, self.last_md5_local = pickle.load(fd)
      fd.close()
      self.trans.retFile(self.mt_file)
      fd = open(self.mt_file)
      self.last, self.last_md5 = pickle.load(fd)
      fd.close()
    except:
      self.last_local, self.last_md5_local = {}, {}
      self.last, self.last_md5 = {}, {}
    self.now, self.now_md5 = {}, {}
    os.path.walk('.', self._osWalkCallback, None)

  def _osWalkCallback(self, dummy, dir, names):
    """
    Parcourt les fichiers pour récupérer leur mtime.
    """
    if dir[-3:] != 'CVS' and dir.find('.svn') == -1 and dir.find('/#') == -1:
      for name in names:
        filename = os.path.join(dir, name)
        if name in ['CVS', '.svn', self.mt_file]:
          continue
        elif name[-1] == '~':
          continue
        elif name[0] == '#':
          continue
        elif os.path.isdir(filename):
          continue
        else:
          stamp = os.stat(filename).st_mtime
          self.now[filename] = stamp
          if filename.endswith('.html') or filename.endswith('.htm') or filename.endswith('.png')or filename.endswith('.conf_general.py') or filename.endswith('.database'):
            fd = open(filename, 'rb')
            self.now_md5[filename] = hashlib.md5(fd.read()).hexdigest()
            fd.close()

  def getNewFiles(self):
    """
    Construit la liste des fichiers à uploader.
    @return: liste des fichiers à uloader
    """
    new = []
    for file in self.now.keys():
      if not self.last.has_key(file):
        new.append(file)
      elif self.last[file] < self.now[file]:
        if self.last_md5.has_key(file) and self.now_md5.has_key(file) and self.now_md5[file] != self.last_md5[file] or not self.last_md5.has_key(file) or not self.now_md5.has_key(file):
          new.append(file)
    return new

  def getNewFilesToDownload(self):
    """
    Construit la liste des fichiers à downloader.
    @return: liste des fichiers à downloader
    """
    new = []
    for file in self.last.keys():
      if not self.now.has_key(file):
        new.append(file)
      elif (self.last_md5.has_key(file) and self.now_md5.has_key(file) and self.last_md5[file] != self.now_md5[file] or (not self.last_md5.has_key(file) or not self.now_md5.has_key(file))) and self.now[file] < self.last[file]:
        if self.last_md5_local.has_key(file) and self.now_md5.has_key(file) and self.last_md5_local[file] != self.now_md5[file] or (not self.last_md5_local.has_key(file) or not self.now_md5.has_key(file)) and self.last_local.has_key(file) and self.now[file] > self.last_local[file]:
          self.conflict = True
        new.append(file)
    return new

  def get_conflict(self):
    """
    Dit si un conflit a été detecté par getNewFilesToDownload.
    @return: True en cas de conflit, False sinon
    """
    return self.conflict

  def save(self):
    """
    Sauvegarde la liste des fichiers à uploader (en supposant qu'ils l'ont bien été)
    pour ne pas avoir à les renvoyer la prochaine fois s'ils ne sont pas modifiés d'ici là.
    """
    fd = open(self.mt_file, 'w')
    pickle.dump((self.now, self.now_md5), fd)
    fd.close()
    self.trans.sendFile(self.mt_file)


def synchronize(db, confirmation=False):
  """
  Fonction en charge de réaliser la synchronisation FTP (et plus tard SSH) avec le serveur distant.
  Effectue effectivement la synchronisation avec le FTP dont les paramètres se trouvent dans conf.
  Lève une exception SyncError en cas de problème.
  @type confirmation: bool
  @param confirmation: confirmation d'ecrasement des fichiers locaux en cas de conflit
  """
  print "<ul><li>"+_("Génération dut site")+"</li>"
  generate.generate_site(db)
  last_cwd = os.getcwd()
  try:
    if conf_private.transfer_mode == 'SSH':
      trans = _transferer_SSH()
    else:
      print "<li>"+_("Connection au serveur FTP")+"</li>"
      trans = _transferer_FTP()
    try:
      os.chdir(confstatic.generate_path)
      find = _finder(trans)
      files_to_download = find.getNewFilesToDownload()
      if find.get_conflict() and not confirmation:
        raise SyncError(_("Conflit entre les fichiers locaux et distants."), True)
      print "<li>"+_("Récupération des fichiers distants plus récents")+"</li><ul>"
      for f in files_to_download:
        trans.retFile(f)
      print "</ul><li>"+_("Envoi des fichiers locaux")+"</li><ul>"
      for f in find.getNewFiles():
        trans.sendFile(f)
      print "</ul>"
      find.save()
      print "</ul>"
    except SyncError, e:
      trans.quit()
      raise e
    trans.quit()
  except SyncError, e:
    os.chdir(last_cwd)
    generate.clean()
    raise e
  os.chdir(last_cwd)
  generate.clean()
