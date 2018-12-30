# ConvertToHugo

Convert your blog from [Jekyll](https://jekyllrb.com/) to [Hugo](http://gohugo.io/).

## Usage:

```
python ConvertToHugo.py jekyll-post-dir output-dir
```

Enhancements compared to the upstream:

1. Keep front matter ordering [require CPython 3.6]
1. Use `bytes` to leave unmodified content untouched
1. Move info string of a fenced code block to end of block
    * Prefixed with `CVT2HUGO: `, which requires to be modified into shortcodes

New Features (octopress and logdown.com specific):

1. Dump metadata from logdown.com
    * Navigate to article list in logdown.com
    * Paste the logdown-metadata.js into the browser console
    * Save the output as json to `logdown.meta`
1. Populate `draft: true` for all unpublished posts, incl. `draft` and `private` posts
    * By reading `logdown.meta`, populate that field
1. Convert `date` field to local timezone-aware `date`
    * Assumption: the `date` is in `yyyy-mm-dd HH:MM` format in UTC without timezone information
    * All `date` are convert into local timezone
