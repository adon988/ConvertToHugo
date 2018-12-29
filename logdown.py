from datetime import datetime, timezone
import json
import re
from typing import Any, Dict

status = {d['title']: d['type'] for d in json.load(open('logdown.meta'))}


def convert_front_matter(fm):  # type: (Dict[str, Any]) -> Dict[str, Any]
    # octopress has no `tags:`, the tags are called `categories:`, thus swap them
    assert 'tags' not in fm
    fm['tags'] = fm['categories']
    del fm['categories']

    # No need to keep the url equal
    del fm['url']
    del fm['comments']

    # Drop empty-value fields
    fm = {k: v for k, v in fm.items() if not (v is None or v in ([], {}))}

    # Convert date format
    fm['date'] = datetime.strptime(fm['date'], '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc).astimezone(None)

    # Populate post status, fetched from logdown.com
    if status[fm['title']] != 'published':
        fm['draft'] = True
    return fm


def convert_body(body):  # type: (bytes) -> bytes
    # convert octopress fenced-code-block
    code = re.compile(
            br'```(?P<lang>[\S]+)[ \t\r\f\v]+(?P<info>[^\r\n]+)(?P<seol>\r\n|\r|\n)'
            br'(?P<body>.+?)'
            br'```(?P<tail>[^\r\n]*?)(?P<teol>\r\n|\r|\n)', re.M | re.S)
    m = code.search(body)
    while m:
        md = m.groupdict()
        body = body.replace(m.group(0), b''.join([
                b'```', md['lang'], md['seol'],
                md['body'],
                b'```', md['tail'], md['teol'],
                b'CVT2HUGO: ', md['info'], md['seol'],
                ]))
        m = code.search(body)
    return body
