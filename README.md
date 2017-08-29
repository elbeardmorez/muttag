
## muttag

### description
python script for performing bulk maintenance on a music library's audio tags

### features
- extract tag info on a dirs/subdirs or files basis

### dependencies
- mutagen

### help

```
Usage: muttag.py [options]

Options:
  -h, --help            show this help message and exit
  -d DIR, --dir=DIR     set DIR to the root music directory
  -f FILES, --files=FILES
                        comma-delimited list of absolute or
                        'pathRoot'-relative music files/paths
  -a, --extract-art     extract album art [mp3 support only]
  -o OUTPUT, --output-info=OUTPUT
                        set OUTPUT as target to dump all tag info to
  -x EXTENSIONS, --extensions=EXTENSIONS
                        EXTENSIONS is a comma delimited list of supported file
                        types
  -v VERBOSITY, --verbosity=VERBOSITY
                        log level. log issues and a subset of tag info to log
                        file (defaulting to stdout)
```

### limitations
- ogg vorbis support only
- no id3v1.1 support

### issues
- some id3 frames (possible id3v1.1) fail to read properly ('[unrepresentable data']). see mutagen [issue 98](https://github.com/quodlibet/mutagen/issues/98)

### todo
- [add] support more formats..
- [imp] deprecate optparse
- [add] delete album art based on dimension
- [add] strip all tag frames/comments except given
- [imp] don't rely on file extentions for type testing
- [imp] make info dump optional and local to target file(s)/dir(s)
- [add] merge generic dump info
- [imp] wildcard file(s)/dir(s) list
- [add] long file url option
- [add] find tags with 'unrepresentable data'
- [add] album art support for ogg
- [imp] extended album art info
- [fix] missing album art for some files
