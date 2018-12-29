#!/usr/bin/env python3.6
import argparse
from datetime import datetime
import os
import re
from typing import Any, Dict

import yaml

import logdown
__author__ = 'coderzh'


def represent_ordereddict(dumper, data):
    value = []
    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)
        value.append((node_key, node_value))
    return yaml.nodes.MappingNode('tag:yaml.org,2002:map', value)


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def convert_front_matter(front_data, post_date, url):
    # type: (Dict[str, Any], datetime, str) -> None
    front_data['url'] = url

    del front_data['layout']

    for tag in ['tags', 'categories', 'category']:
        if tag in front_data and isinstance(front_data[tag], str):
            front_data[tag] = front_data[tag].split(' ')

    if 'category' in front_data:
        front_data['categories'] = front_data['category']
        del front_data['category']


replace_regex_list = [
    # (re.compile(br'^```(.*?)\n(.*?)\n```', re.DOTALL), br'{{< highlight \1 >}}\n\2\n{{< /highlight >}}'),
    (re.compile(br'<!--\smore\s-->'),  b'<!--more-->'),
    (re.compile(br'\{%\sraw\s%\}(.*)\{%\sendraw\s%\}'), br'\1')
]


def convert_body(body):
    # type: (bytes) -> bytes
    result = body
    for regex, replace_with in replace_regex_list:
        result = regex.sub(replace_with, result)
    return result


def write_out_file(front_data, body, out_file_path):
    # type: (Dict[str, Any], bytes, str) -> None
    with open(out_file_path, 'wb') as f:
        f.write(b'---\n')
        yaml.dump(front_data, f, width=1000, default_flow_style=True, allow_unicode=True, Dumper=MyDumper, encoding='utf8')
        f.write(b'---\n')
        f.write(body)


filename_regex = re.compile(r'(\d+-\d+-\d+)-(.*)')


def parse_from_filename(filename):
    slug = os.path.splitext(filename)[0]
    m = filename_regex.match(slug)
    if m:
        slug = m.group(2)
        post_date = datetime.strptime(m.group(1), '%Y-%m-%d')
        return post_date, '/%s/%s/' % (post_date.strftime('%Y/%m/%d'), slug)
    return None, '/' + slug


def convert_post(file_path, out_dir):
    filename = os.path.basename(file_path)
    post_date, url = parse_from_filename(filename)

    with open(file_path, 'rb') as f:
        content = f.readlines()

    head = b''
    for i, l in enumerate(content[1:], 1):
        if l.strip() == b'---':
            bodies = content[i + 1:]
            break
        head += l

    front_data = yaml.safe_load(head.decode())
    if not front_data:
        print('Error load yaml: %s' % file_path)
        return False

    '''
    if 'layout' in front_data:
        if post_date:
            out_dir = os.path.join(out_dir, front_data['layout'], str(post_date.year))
        else:
            out_dir = os.path.join(out_dir, front_data['layout'])
    '''

    out_file_path = os.path.join(out_dir, filename)

    convert_front_matter(front_data, post_date, url)
    front_data = logdown.convert_front_matter(front_data)
    body = convert_body(b''.join(bodies))
    body = logdown.convert_body(body)
    write_out_file(front_data, body, out_file_path)

    return True


def convert(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    error = 0
    for root, dirs, files in os.walk(src_dir):
        for filename in files:
            try:
                if os.path.splitext(filename)[1] != '.md' or filename in ['README.md', 'LICENSE.md']:
                    continue
                file_path = os.path.join(root, filename)
                common_prefix = os.path.commonprefix([src_dir, file_path])
                rel_path = os.path.relpath(os.path.dirname(file_path), common_prefix)
                real_out_dir = os.path.join(out_dir, rel_path)
                if convert_post(file_path, real_out_dir):
                    print('Converted: %s' % file_path)
                    count += 1
                else:
                    error += 1
            except Exception as e:
                error += 1
                print('Error convert: %s \nException: %s' % (file_path, e))

    print('--------\n%d file converted! %s' % (count, 'Error count: %d' % error if error > 0 else 'Congratulation!!!'))


if __name__ == '__main__':
    yaml.add_representer(dict, represent_ordereddict)
    parser = argparse.ArgumentParser(description='Convert Jekyll blog to GoHugo')
    parser.add_argument('src_dir', help='jekyll post dir')
    parser.add_argument('out_dir', help='hugo root path')
    args = parser.parse_args()

    convert(os.path.abspath(args.src_dir), os.path.abspath(args.out_dir))
