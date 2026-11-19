#!/usr/bin/env python3
"""Validate the skill before release. Standard library only, no install step."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = 'humanizer-zh'
SKILL_DIR = ROOT / 'skills' / SKILL_NAME
NAME_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

errors = []
warnings = []


def fail(message):
    errors.append(message)


def parse_frontmatter(text):
    if not text.startswith('---\n'):
        fail('SKILL.md must start with a YAML frontmatter block')
        return {}
    end = text.find('\n---\n', 4)
    if end == -1:
        fail('SKILL.md frontmatter is not closed with ---')
        return {}
    block = text[4:end]
    data, key, block_scalar = {}, None, False
    for line in block.splitlines():
        if not line.strip():
            continue
        indented = line.startswith((' ', '\t'))
        if indented and key and block_scalar:
            data[key] = (data[key] + ' ' + line.strip()).strip()
            continue
        if indented and key and ':' in line:
            nested_key, nested_value = line.split(':', 1)
            data[nested_key.strip()] = nested_value.strip().strip('"')
            continue
        if indented and key:
            data[key] = (data[key] + ' ' + line.strip()).strip()
            continue
        if ':' not in line:
            fail('frontmatter line without a colon: {}'.format(line.strip()))
            continue
        key, value = line.split(':', 1)
        value = value.strip()
        block_scalar = value in ('|', '>')
        data[key.strip()] = '' if block_scalar else value.strip('"')
    return data


def main():
    if not SKILL_DIR.is_dir():
        fail('missing skill directory: skills/{}'.format(SKILL_NAME))
        return report()

    skill_md = SKILL_DIR / 'SKILL.md'
    if not skill_md.is_file():
        fail('missing skills/{}/SKILL.md'.format(SKILL_NAME))
        return report()

    text = skill_md.read_text(encoding='utf-8')
    meta = parse_frontmatter(text)

    name = meta.get('name', '')
    if name != SKILL_NAME:
        fail('frontmatter name {!r} does not match directory {!r}'.format(name, SKILL_NAME))
    if not NAME_RE.match(name or ''):
        fail('name must be lowercase letters, digits and single hyphens: {!r}'.format(name))

    description = meta.get('description', '')
    if not description:
        fail('description is required; it decides whether the skill ever loads')
    elif len(description) > 1024:
        fail('description is {} characters, limit is 1024'.format(len(description)))
    if description and not re.search(r'用于|Use when|当需要', description):
        warnings.append('description has no "used when" clause; routing may be vague')

    version = meta.get('version', '')
    package = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))
    if version and version != package.get('version'):
        fail('metadata.version {} != package.json version {}'.format(version, package.get('version')))
    if not version:
        warnings.append('SKILL.md metadata.version is not set')

    changelog = ROOT / 'CHANGELOG.md'
    if not changelog.is_file():
        fail('missing CHANGELOG.md')
    else:
        head = re.search(r'^##\s*\[?(\d+\.\d+\.\d+)', changelog.read_text(encoding='utf-8'), re.M)
        if not head:
            fail('CHANGELOG.md has no "## [x.y.z]" heading')
        elif head.group(1) != package.get('version'):
            fail('CHANGELOG.md top entry {} != package.json version {}'.format(
                head.group(1), package.get('version')))

    # Relative links and code spans that point inside the skill must exist.
    for target in re.findall(r'\]\(([^)#:]+\.md)\)', text):
        if not (SKILL_DIR / target).exists():
            fail('SKILL.md links to a missing file: {}'.format(target))
    for target in re.findall(r'`((?:references|scripts|assets)/[^`]+)`', text):
        if not (SKILL_DIR / target).exists():
            fail('SKILL.md refers to a missing file: {}'.format(target))

    for path in SKILL_DIR.rglob('*'):
        if path.is_symlink():
            fail('symlink inside the skill will not survive packaging: {}'.format(path.relative_to(ROOT)))
        elif path.is_file() and (path.suffix == '.pyc' or '__pycache__' in path.parts):
            fail('build artifact inside the skill: {}'.format(path.relative_to(ROOT)))

    # Translation parity: the numbering is the anchor other docs quote.
    groups = re.findall(r'^## ([A-F])\. ', text, re.M)
    if groups != list('ABCDEF'):
        fail('expected sections A-F in order, found {}'.format(groups or 'none'))
    numbers = [int(n) for n in re.findall(r'^### (\d+)\. ', text, re.M)]
    if numbers != list(range(1, 27)):
        print('found sections: {}'.format(numbers))
        fail('expected sections 1-26 in order, found {}'.format(len(numbers)))

    if '\u2014' in text.replace('\u2014\u2014', '') and '§8' not in text:
        warnings.append('em dashes present but section 8 is missing')

    if len(text.splitlines()) < 200:
        warnings.append('translation looks shorter than the 407-line original; check for dropped sections')

    return report()


def report():
    for message in warnings:
        print('warning: ' + message)
    for message in errors:
        print('error: ' + message)
    if errors:
        print('\n{} error(s)'.format(len(errors)))
        return 1
    print('ok: {}'.format(SKILL_NAME))
    return 0


if __name__ == '__main__':
    sys.exit(main())
