#!/usr/bin/python

#system
import sys
import os
import codecs
import string
import re
import filecmp
from optparse import OptionParser # deprecated

#local
import mutagen.mp3 as mp3
import mutagen.id3 as id3
import mutagen.oggvorbis as oggvorbis

apictypes = {
  0 : "Other",
  1 : "32x32 pixels 'file icon' (PNG only)",
  2 : "Other file icon",
  3 : "Cover (front)",
  4 : "Cover (back)",
  5 : "Leaflet page",
  6 : "Media (e.g. label side of CD)",
  7 : "Lead artist/lead performer/soloist",
  8 : "Artist/performer",
  9 : "Conductor",
  10 : "Band/Orchestra",
  11 : "Composer",
  12 : "Lyricist/text writer",
  13 : "Recording Location",
  14 : "During recording",
  15 : "During performance",
  16 : "Movie/video screen capture",
  17 : "A bright coloured fish",
  18 : "Illustration",
  19 : "Band/artist logotype",
  20 : "Publisher/Studio logotype"
}

def imagetype(type):
  if type == "jpeg":
    return "jpg"
  else:
    return type

def apictype(type):
  if type == 3:
    return "front"
  elif type == 4:
    return "back"
  elif type == 5:
    return "leaflet"
  elif type == 6:
    return "media"
  elif type >= 0 and type <= len(apictypes):
    return apictypes[type]
  else:
    return "unknown"

def log(arg, file = 1):
  if file == 1:
    sys.stdout.write(arg + "\n")
  elif file == 2:
    sys.stderr.write(arg + "\n")

def info(file):
  options.verbosity > 2 and log("[debug info]")
  f = os.fdopen(os.open(file, os.O_RDONLY))
  s = None
  try:
    if re.match(".*mp3$", file):
      info = mp3.MP3(file)
    elif re.match(".*ogg$", file):
      info = oggvorbis.OggVorbis(file)
    s = info.pprint() if options.verbosity > 1 else info.info.pprint()
  except: pass
  finally: f.close()
  return s

def art(file):
  options.verbosity > 2 and log("[debug art]")

  s = ""
  if not re.match(".*mp3$", file):
    return s

  try:
    tag = id3.ID3()
    tag.load(file, translate = True) # force id3 v2.4 translation
    s = tag.pprint()
    for frame in tag.getall('APIC'):
      fPath = os.path.dirname(file)
      fName = apictype(frame.type)
      fType = imagetype(frame.mime.split(u'/')[1])
      fPathFile = fPath + os.sep + fName + u'.' + fType
      l = 0
      if os.path.exists(fPathFile):
        l = 2
        while os.path.exists(fPath + os.sep + fName + str(l) + u'.' + fType):
          l += 1
        fPathFile = fPath + os.sep + fName + str(l) + u'.' + fType
      f = os.open(fPathFile, os.O_CREAT + os.O_WRONLY)
      try:
        os.ftruncate(f, 0)
        f = os.fdopen(f, 'w')
        f.write(frame.data)
      except Exception: pass
      finally: f.close()
      # remove if dupe
      if l > 0:
        if filecmp.cmp(fPathFile, fPath + os.sep + fName + u'.' + fType):
          log(u'[debug] deleting duplicate image')
          os.remove(fPathFile)
        else:
          for ll in range(2, l):
            if filecmp.cmp(fPathFile, fPath + os.sep + fName + str(ll) + u'.' + fType):
              log(u'[debug] deleting duplicate image')
              os.remove(fPathFile)
              break
  except: pass
  return s

def process(file, output):
  bRet = None

  # info
  s = info(file)
  if s and s != "":
    bRet = True;
    options.verbosity and log(file.split(os.sep)[-1] + u'\n' + s)
    output.write(file.split(os.sep)[-1] + u'\n' + s + u'\n')

  # album art
  if options.extractart:
    s = file.split(os.sep)[-1].decode('utf-8')
    if art(file):
      s = s + u'\n' "album art extracted successfully"
    else:
      s = s + u'\n' "album art extraction failed"
    options.verbosity and log(s.decode('utf-8'))
    output.write(s.decode('utf-8') + u'\n')
    bRet = True

  return bRet

#args
optionParser = OptionParser()
def optionsListCallback(option, opt, value, parser):
  if value == "":
    setattr(optionParser.values, option.dest, None)
  else:
    setattr(optionParser.values, option.dest,
            map(lambda s: string.replace(s.rstrip(","), "\\,", ","), re.findall("(.*?[^\\\],|.+$)", value)))
def optionsPathExpansionCallback(option, opt, value, parser):
  setattr(optionParser.values, option.dest, os.path.expandvars(os.path.expanduser(value).split('|')))
optionParser.add_option("-d", "--dir", metavar = "DIR",
                        type = "string", dest = "pathRoot", default = os.path.curdir,
                        action = "callback", callback = optionsPathExpansionCallback,
                        help = "set DIR to the root music directory")
optionParser.add_option("-f", "--files", metavar = "FILES",
                        type = "string", dest = "pathFiles", default = "",
                        action = "callback", callback = optionsPathExpansionCallback,
                        help = "comma-delimited list of absolute or 'pathRoot'-relative music files/paths")
optionParser.add_option("-a", "--extract-art",
                        dest = "extractart", default = False,
                        action = "store_true",
                        help = "extract album art [mp3 support only]"),
optionParser.add_option("-o", "--output-info", metavar = "OUTPUT",
                        type = "string", dest = "output", default = "./muttag.info",
                        help = "set OUTPUT as target to dump all tag info to")
optionParser.add_option('-x', '--extensions', metavar = "EXTENSIONS",
                        type = "string", dest = "extensions", default = (".mp3", ".ogg"),
                        action = "callback", callback = optionsListCallback,
                        help = "EXTENSIONS is a comma delimited list of supported file types")
optionParser.add_option("-v", "--verbosity", metavar = "VERBOSITY",
                        type = "int", dest = "verbosity", default = 1,
                        action = "store",
                        help = "log level. log issues and a subset of tag info to log file (defaulting to stdout)")

(options, args) = optionParser.parse_args() # options is a 'dict', args a 'list'

#process
try:

  if options.verbosity > 1:
    log("[debug] verbosity level: " + str(options.verbosity))
    log("[debug] parsed args:")
    l = 0
    for name, value in options.__dict__.items():
      log( "idx: " + str(l) + ": '" + name + ": '" + str(value) + "'")
      l += 1

    log("[debug] unparsed args:")
    l = 0
    for value in args:
      log("idx: " + str(l) + ": '" + str(value) + "'")
      l += 1

  #output file
  f = codecs.open(options.output, 'w', 'utf-8')
  f.truncate()

  list = options.pathFiles or options.pathRoot
  options.verbosity > 2 and log('[debug] dumping file list')
  try:
    for path in list:
      if not os.path.exists(path) and os.path.exists(options.pathRoot[0] + os.path.sep + path):
        path = options.pathRoot[0] + os.path.sep + path
      if not os.path.exists(path):
        continue

      if os.path.isfile(path):
        if path.endswith(options.extensions):
          if process(path, f):
            f.write(u'----------------------\n')
            options.verbosity and log(u'----------------------')
      else:
        #dump file list
        l = 0
        for root, subdir, files in os.walk(path):
          if len(files) > 0:
            root = root.decode('utf-8');
            header = u'location: ' + os.path.abspath(root).decode('utf-8')
            f.write(u'=' * len(header) + u'\n')
            f.write(header.decode('utf-8') + u'\n')
            f.write(u'=' * len(header) + u'\n')
            options.verbosity and log(u'=' * (len(header)))
            options.verbosity and log(header.decode('utf-8'))
            options.verbosity and log(u'=' * (len(header)))
            for file in sorted(files):
              if file.endswith(options.extensions):
                if process(os.path.join(root, file.decode('utf-8')), f):
                  l += 1
                  f.write(u'----------------------\n')
                  options.verbosity and log(u'----------------------')

  except Exception as e:
    print e
  finally: f.close()
except Exception as e:
  print e
