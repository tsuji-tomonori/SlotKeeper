#!/usr/bin/env python3
"""導入先adapter契約と生成物を言語非依存で検査する。commandは信頼するrepository code。"""
from __future__ import annotations

import argparse
import csv
import html
import importlib.util
import io
import json
import os
import re
import shutil
import string
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

# -Iでも配布済みの同じSkill内moduleだけを解決する。
_HELPER = Path(__file__).resolve().with_name('reference_inventory.py')
if _HELPER.is_symlink():
    raise ValueError('symlink helper is not allowed')
_SPEC = importlib.util.spec_from_file_location('design_reference_inventory', _HELPER)
assert _SPEC and _SPEC.loader
_INVENTORY = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_INVENTORY)
ASSETS = _INVENTORY.ASSETS
confined = _INVENTORY.confined
read_json = _INVENTORY.read_json
validate_inventory = _INVENTORY.validate_inventory
validate_schema = _INVENTORY.validate_schema

SURFACES = {'api', 'data', 'infra', 'frontend'}
API_DOCUMENTS = {'detail-design', 'interface', 'messages', 'query', 'sequence', 'unit-test'}


def strings(value, label: str, empty: bool = False) -> list[str]:
    """重複しない文字列集合を確認する。"""
    validate_schema(value, {'type': 'array', 'items': {'type': 'string', 'minLength': 1}, 'minItems': 0 if empty else 1, 'uniqueItems': True}, label)
    return value


def tree_snapshot(root: Path, prefix: str) -> dict[str, bytes]:
    """所有root内の全fileを取り込み、directory置換・linkを拒否する。"""
    directory = confined(root, prefix)
    if not directory.is_dir():
        raise ValueError(f'output root must be directory: {prefix}')
    result = {}
    for path in sorted(directory.rglob('*')):
        relative = path.relative_to(root).as_posix()
        confined(root, relative)
        if path.is_file():
            result[relative] = path.read_bytes()
        elif not path.is_dir():
            raise ValueError(f'nonregular output: {relative}')
    return result


def snapshot(root: Path, capabilities: dict) -> dict[str, bytes]:
    """明示一覧と出力rootの完全一致により旧生成物も検出する。"""
    result = {}
    roots = []
    for name, cap in capabilities.items():
        if cap['status'] != 'required':
            continue
        prefix = cap['output_root']
        output_root = confined(root, prefix)
        if any(output_root.is_relative_to(p) or p.is_relative_to(output_root) for p in roots):
            raise ValueError('overlapping output ownership')
        roots.append(output_root)
        expected = set(strings(cap['outputs'], f'{name}.outputs'))
        for path in expected:
            if not confined(root, path).is_relative_to(output_root):
                raise ValueError(f'unmanaged output path: {path}')
        actual = tree_snapshot(root, prefix)
        allowed_dirs = {parent for path in expected for parent in confined(root, path).parents if parent.is_relative_to(output_root)}
        if any(p.is_dir() and p not in allowed_dirs for p in output_root.rglob('*')):
            raise ValueError('stale undeclared output directory')
        if set(actual) != expected:
            raise ValueError(f'stale or missing outputs: {sorted(set(actual) ^ expected)}')
        if not any(p.endswith('.md') and body.strip() for p, body in actual.items()):
            raise ValueError(f'{name}: nonempty Markdown design required')
        if any(not body.strip() for body in actual.values()):
            raise ValueError(f'{name}: empty output')
        result.update(actual)
    return result


def headings(content: str) -> list[tuple[int, str]]:
    """コードfenceを除いたATX見出しだけを読む。"""
    result = []
    fence = None
    for line in content.splitlines():
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            continue
        match = re.match(r'^(#{1,6})\s+(.+?)\s*#*$', line)
        if match and fence is None:
            result.append((len(match[1]), match[2]))
    return result


def markdown_targets(text: str, source: str) -> list[str]:
    """生成文書のリンク構文を走査し、未対応の明示リンクを位置付きで拒否する。"""
    def fail(position: int) -> None:
        line = text.count('\n', 0, position) + 1
        raise ValueError(f'unsupported or malformed Markdown link: {source}:{line}')

    def decode(value: str) -> str:
        return html.unescape(re.sub(r'\\([!"#$%&\'()*+,\-./:;<=>?@\[\]\\^_`{|}~])', r'\1', value))

    def label(value: str) -> str:
        return ' '.join(value.split()).casefold()

    def skip_space(position: int) -> int:
        while position < len(text) and text[position].isspace():
            position += 1
        return position

    def code_end(position: int) -> int:
        run = re.match(r'`+', text[position:])[0]
        end = re.search(r'(?<!`)' + re.escape(run) + r'(?!`)', text[position + len(run):])
        return position + len(run) + (end.end() if end else 0)

    def quoted(position: int, closing: str) -> int:
        start = position
        position += 1
        while position < len(text):
            if text[position] == '\\' and position + 1 < len(text):
                position += 2
            elif text[position] == closing:
                return position + 1
            elif text[position] == '\n' and closing == '>':
                fail(start)
            else:
                position += 1
        fail(start)

    def destination(position: int, inline: bool) -> tuple[str, int]:
        start = position
        position = skip_space(position)
        if position < len(text) and text[position] == '<':
            end = quoted(position, '>')
            target = text[position + 1:end - 1]
            position = end
        else:
            begin = position
            depth = 0
            while position < len(text):
                char = text[position]
                if char == '\\' and position + 1 < len(text):
                    position += 2
                    continue
                if char.isspace() or (char == ')' and depth == 0):
                    break
                if char in '<>':
                    fail(start)
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                position += 1
            if depth:
                fail(start)
            target = text[begin:position]
        spaced = skip_space(position)
        if spaced > position and spaced < len(text) and text[spaced] in '\"\'(':
            position = quoted(spaced, ')' if text[spaced] == '(' else text[spaced])
        if inline:
            position = skip_space(position)
            if position >= len(text) or text[position] != ')':
                fail(start)
            position += 1
        else:
            while position < len(text) and text[position] in ' \t':
                position += 1
            if position < len(text) and text[position] != '\n':
                fail(start)
        return decode(target), position

    # fenceは同種かつ同じ長さ以上の閉じmarkerまで除外する。
    lines = text.splitlines(keepends=True)
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line.rstrip('\n'))
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            lines[index] = '\n' if line.endswith('\n') else ''
        elif marker:
            fence = marker[1]
            lines[index] = '\n' if line.endswith('\n') else ''
    text = ''.join(lines)
    definitions = {}
    spans = []
    for match in re.finditer(r'(?m)^ {0,3}\[((?:\\.|[^\]\\\n])+)\]:', text):
        if any(start <= match.start() < end for start, end in spans):
            continue
        target, end = destination(match.end(), inline=False)
        definitions.setdefault(label(match[1]), target)
        spans.append((match.start(), end))
    # 定義を同じ長さの空白へ置換し、参照本文だけを走査する。
    for start, end in reversed(spans):
        text = text[:start] + re.sub(r'[^\n]', ' ', text[start:end]) + text[end:]
    targets = []
    position = 0
    while position < len(text):
        char = text[position]
        if char == '\\':
            position += 2
            continue
        if char == '`':
            position = code_end(position)
            continue
        if char == '<' and re.match(r'<(?:a|img)\b', text[position:], re.I):
            fail(position)
        if char != '[':
            position += 1
            continue
        start = position
        depth = 1
        position += 1
        while position < len(text) and depth:
            if text[position] == '`':
                position = code_end(position)
                continue
            if text[position] == '\\':
                position += 2
                continue
            if text[position] == '[':
                depth += 1
            elif text[position] == ']':
                depth -= 1
            position += 1
        if depth:
            if '](' in text[start:] or '][' in text[start:]:
                fail(start)
            break
        name = text[start + 1:position - 1]
        if '[' in name:
            # リンクlabel内の画像などにも独立した宛先がある。
            targets.extend(markdown_targets(name, source))
        if position < len(text) and text[position] == '(':
            target, position = destination(position + 1, inline=True)
            targets.append(target)
        elif position < len(text) and text[position] == '[':
            end = text.find(']', position + 1)
            if end < 0:
                fail(position)
            key = label(text[position + 1:end] or name)
            if key not in definitions:
                raise ValueError(f'broken reference link: {source} [{key}]')
            targets.append(definitions[key])
            position = end + 1
        elif position < len(text) and text[position] == ':':
            # blockquote/list内の参照定義等は未対応として黙殺しない。
            fail(start)
        elif label(name) in definitions:
            targets.append(definitions[label(name)])
    return targets


def local_links(root: Path, source: str) -> set[str]:
    """Markdownの相対file/fragmentリンクを検査する（外部URLは取得しない）。"""
    path = confined(root, source)
    text = path.read_text(encoding='utf-8')
    targets = markdown_targets(text, source)
    resolved = set()
    for target in targets:
        url = urlsplit(target)
        if url.scheme or url.netloc:
            continue
        if url.path.startswith('/'):
            raise ValueError(f'absolute document link: {target}')
        destination = path.parent / unquote(url.path) if url.path else path
        # 正常な親indexへの ../ は正規化後に境界とsymlinkを検査する。
        for parent in [destination, *destination.parents]:
            if parent.is_symlink():
                raise ValueError(f'symlink link: {target}')
        destination = destination.resolve()
        if not destination.is_relative_to(root):
            raise ValueError(f'link escapes repository: {target}')
        relative = destination.relative_to(root).as_posix()
        if not confined(root, relative).is_file():
            raise ValueError(f'broken link: {source} -> {target}')
        if url.fragment:
            anchors = {re.sub(r'[^\w\- ]', '', title.lower()).replace(' ', '-') for _, title in headings(destination.read_text(encoding='utf-8'))}
            if unquote(url.fragment) not in anchors:
                raise ValueError(f'broken fragment: {source} -> {target}')
        resolved.add(relative)
    return resolved


def validate_profile(profile: dict) -> None:
    """構成grammarの型と版の同一性を検査し、空値による検査回避を拒否する。"""
    validate_schema(profile, read_json(ASSETS / 'api-document-profile.schema.json'), 'profile')

    def fields(template: str, expected: list[str]) -> None:
        parts = list(string.Formatter().parse(template))
        actual = [field for _, field, _, _ in parts if field is not None]
        if sorted(actual) != sorted(expected) or any(spec or conversion for _, _, spec, conversion in parts):
            raise ValueError('profile: invalid template fields')

    fields(profile['layout'], ['group', 'api', 'kind'])
    confined(Path('/profile'), profile['layout'].format(group='group', api='api', kind='kind'))
    fields(profile['non_applicable'], ['reason'])
    for grammar in profile['headings'].values():
        repeats = set()
        for section in grammar:
            if 'repeat' not in section:
                continue
            if section['repeat'] in repeats:
                raise ValueError('profile: duplicate repeat key')
            repeats.add(section['repeat'])
            if any(child['level'] <= section['level'] for child in section['children']):
                raise ValueError('profile: child level must be deeper than repeat level')
            if section['min'] == 0 and 'empty' not in section:
                raise ValueError('profile: optional repeat requires not-applicable expression')
            if 'empty' in section:
                fields(section['empty'], ['reason'])
    canonical = read_json(ASSETS / 'api-document-profile-v1.json')
    if (profile['id'], profile['version']) == (canonical['id'], canonical['version']):
        for key in ('reference', 'layout', 'headings', 'non_applicable'):
            if profile[key] != canonical[key]:
                raise ValueError(f'profile: changed published version contract: {key}')


def check_api(root: Path, api: dict, outputs: set[str]) -> None:
    """operation集合・6帳票の章順・階層とindexを検査する。"""
    profile = read_json(confined(root, api['profile']))
    validate_profile(profile)
    actual_operations = read_json(confined(root, api['operation_inventory']))
    identities = [x['id'] for x in api['operations']]
    strings(actual_operations, 'operation inventory')
    if len(set(identities)) != len(identities) or set(identities) != set(actual_operations):
        raise ValueError('operation inventory mismatch')
    groups = {op['group'] for op in api['operations']}
    if set(api['group_indexes']) != groups or set(api['api_indexes']) != set(identities):
        raise ValueError('hierarchy indexes mismatch')
    expected_indexes = {api['index'], *api['group_indexes'].values(), *api['api_indexes'].values()}
    if not expected_indexes <= outputs or api['index'] != f"{api['root']}/index.md":
        raise ValueError('missing root/group/API index')
    if not set(api['group_indexes'].values()) <= local_links(root, api['index']):
        raise ValueError('root index missing group link')
    documents = []
    for op in api['operations']:
        if '/' in op['group'] or '/' in op['api']:
            raise ValueError('group/API must be one path component')
        directory = f"{api['root']}/{op['group']}/{op['api']}"
        group_index = f"{api['root']}/{op['group']}/index.md"
        api_index = directory+'/index.md'
        if api['group_indexes'][op['group']] != group_index or api['api_indexes'][op['id']] != api_index:
            raise ValueError('invalid group/API hierarchy')
        if api_index not in local_links(root, group_index) or not set(op['documents'].values()) <= local_links(root, api_index):
            raise ValueError('index missing API/document link')
        for kind, filename in op['documents'].items():
            expected_path = api['root']+'/'+profile['layout'].format(group=op['group'], api=op['api'], kind=kind)
            if filename != expected_path or filename not in outputs:
                raise ValueError('document layout or ownership mismatch')
            documents.append(filename)
            body = confined(root, filename).read_text(encoding='utf-8')
            found = headings(body)
            if not found or found[0][0] != 1 or sum(level == 1 for level, _ in found) != 1:
                raise ValueError('document requires exactly one title')
            expected = []
            for section in profile['headings'][kind]:
                if 'repeat' not in section:
                    expected.append((section['level'], section['title']))
                    continue
                key = section['repeat']
                values = strings(op['sections'].get(key), 'repeated sections '+key, empty=True)
                if len(values) < section.get('min', 0):
                    raise ValueError('missing repeated section: '+key)
                if not values:
                    reason = op.get('non_applicable', {}).get(key, '')
                    if not reason.strip() or section.get('empty', '').format(reason=reason) not in body:
                        raise ValueError('empty section needs explicit not-applicable reason: '+key)
                for value in values:
                    expected.append((section['level'], value))
                    expected.extend((child['level'], child['title']) for child in section['children'])
            if found[1:] != expected:
                raise ValueError(f'chapter missing/order/duplicate: {filename}')
            if kind == 'sequence' and 'sequenceDiagram' not in body:
                raise ValueError('sequence diagram missing')
    if len(documents) != len(set(documents)):
        raise ValueError('duplicate operation document')


def crud_renderings(model: dict) -> dict[str, bytes]:
    """同じ言語非依存CRUDモデルからCSV・表・図・根拠を決定的に射影する。"""
    if set(model) != {'schema_version', 'operations', 'rows', 'no_access', 'unresolved'} or model['schema_version'] != 1:
        raise ValueError('invalid CRUD model')
    operations = set(strings(model['operations'], 'CRUD operations'))
    if model['unresolved']:
        raise ValueError('unresolved CRUD is not no-access')
    rows = model['rows']
    pairs = set()
    for row in rows:
        if set(row) != {'operation', 'resource', 'access', 'evidence'} or row['operation'] not in operations or not row['resource']:
            raise ValueError('invalid CRUD row')
        if re.search(r'[\n\r|"<>]', row['operation']+row['resource']):
            raise ValueError('unsafe CRUD label')
        access = strings(row['access'], 'CRUD access')
        if not set(access) <= set('CRUD') or not row['evidence']:
            raise ValueError('invalid CRUD access/evidence')
        pair = (row['operation'], row['resource'])
        if pair in pairs:
            raise ValueError('duplicate CRUD pair')
        pairs.add(pair)
        for evidence in row['evidence']:
            if set(evidence) != {'path', 'line', 'role'} or evidence['role'] not in {'read', 'write'} or type(evidence['line']) is not int or evidence['line'] < 1:
                raise ValueError('invalid CRUD evidence')
        roles = {e['role'] for e in row['evidence']}
        if ('R' in access and 'read' not in roles) or (set(access) & set('CUD') and 'write' not in roles):
            raise ValueError('CRUD read/write evidence mismatch')
    accessed = {r['operation'] for r in rows}
    if not isinstance(model['no_access'], dict) or any(not isinstance(v, str) or not v.strip() for v in model['no_access'].values()):
        raise ValueError('no-access reason required')
    if accessed & model['no_access'].keys() or accessed | model['no_access'].keys() != operations:
        raise ValueError('CRUD operation coverage mismatch')
    items = [(r['operation'], r['resource'], ''.join(c for c in 'CRUD' if c in r['access'])) for r in rows]
    items += [(op, '-', 'NONE') for op in model['no_access']]
    items.sort()
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(['operation', 'resource', 'access'])
    writer.writerows(items)
    table = '# API×保存先 CRUD\n\n| operation | resource | access |\n|---|---|---|\n'
    table += ''.join(f'| {op} | {res} | {access} |\n' for op, res, access in items)
    diagram = ['flowchart LR']
    for i, (op, resource, access) in enumerate(items):
        diagram += [f'  a{i}["{op}"] -->|{access}| r{i}["{resource}"]']
    return {'csv': buffer.getvalue().encode(), 'table': table.encode(), 'diagram': ('\n'.join(diagram)+'\n').encode(),
            'evidence': (json.dumps(model, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode()}


def validate_outputs(root: Path, data: dict, output: dict[str, bytes]) -> None:
    """形式的な適合とadapterの意味的検査結果を分けて確認する。"""
    for path in output:
        if path.endswith('.md'):
            local_links(root, path)
    for name, cap in data['capabilities'].items():
        if cap['status'] != 'required':
            continue
        if cap['report'] not in output:
            raise ValueError('report must be owned output')
        report = read_json(confined(root, cap['report']))
        if set(report) != {'configuration', 'design_drift', 'execution_tests', 'unsupported_surfaces'}:
            raise ValueError('report must separate configuration/design_drift/execution_tests/unsupported_surfaces')
        if report['configuration'] != 'pass' or report['design_drift'] != 'pass' or report['execution_tests'] not in {'pass', 'not-run'}:
            raise ValueError(f'{name}: failed adapter report')
        if report['unsupported_surfaces'] != []:
            raise ValueError(f'{name}: unsupported surface remains incomplete')
    if data['surfaces']['api']['status'] == 'required':
        if 'api' not in data or 'crud' not in data:
            raise ValueError('API requires profile/hierarchy and CRUD (including no-access)')
        check_api(root, data['api'], set(output))
    if 'crud' in data:
        config = data['crud']
        if not set(config.values()) <= output.keys():
            raise ValueError('CRUD files must be owned outputs')
        model = read_json(confined(root, config['model']))
        if 'api' in data and set(model['operations']) != {op['id'] for op in data['api']['operations']}:
            raise ValueError('CRUD/API operation mismatch')
        rendered = crud_renderings(model)
        for row in model['rows']:
            for evidence in row['evidence']:
                source = confined(root, evidence['path'])
                if not source.is_file() or evidence['line'] > len(source.read_text(encoding='utf-8').splitlines()):
                    raise ValueError('CRUD evidence source is missing')
        for kind, body in rendered.items():
            if output[config[kind]] != body:
                raise ValueError(f'CRUD {kind} differs from common model')


def repository_snapshot(root: Path) -> dict:
    """file bytes・directory・symlink targetを含む作業treeの同一性を確認する。"""
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(directory)/name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[relative] = ('symlink', os.readlink(path))
            elif path.is_dir():
                result[relative] = ('directory',)
            elif path.is_file():
                result[relative] = ('file', path.read_bytes())
            else:
                raise ValueError(f'nonregular repository entry: {relative}')
    return result


def check(root: Path, contract: str) -> dict:
    """既存出力を保持したまま作業用コピーでcheckと二重生成を実行する。"""
    root = root.resolve(strict=True)
    data = read_json(confined(root, contract))
    validate_schema(data, read_json(ASSETS / 'adapter-manifest.schema.json'))
    active = {x['id'] for x in read_json(confined(root, data['requirements']))['requirements'] if x['status'] == 'active'}
    applicable = set(data['applicable_requirement_ids'])
    mapped = {r for cap in data['capabilities'].values() for r in cap['requirement_ids']}
    if applicable != mapped or not applicable <= active:
        raise ValueError('unknown/inactive/unmapped/excess requirement IDs')
    if not SURFACES <= data['surfaces'].keys():
        raise ValueError('classify api, data, infra and frontend')
    for name, surface in data['surfaces'].items():
        if surface['status'] == 'not-applicable':
            if not surface.get('reason', '').strip():
                raise ValueError(f'{name}: not-applicable requires reason')
        else:
            for cap in strings(surface.get('capabilities'), name+'.capabilities'):
                if cap not in data['capabilities'] or data['capabilities'][cap]['status'] != 'required':
                    raise ValueError('surface has missing/unsupported capability')
    required_fields = {'sources', 'generate', 'check', 'output_root', 'outputs', 'report'}
    for name, cap in data['capabilities'].items():
        if cap['status'] == 'not-applicable':
            if not cap.get('reason', '').strip():
                raise ValueError('not-applicable capability requires reason')
            continue
        if not required_fields <= cap.keys() or '--check' not in cap['check']:
            raise ValueError('capability requires generation, --check, sources and owned outputs')
        for source in cap['sources']:
            path = confined(root, source)
            if not path.exists():
                raise ValueError(f'missing source: {source}')
            if path.is_dir():
                for child in path.rglob('*'):
                    confined(root, child.relative_to(root).as_posix())
    inventory_coverage = set()
    for inventory in data['reference_inventories']:
        item = read_json(confined(root, inventory))
        validate_inventory(item, active, target_root=root)
        if item['scope'] != 'target-adoption':
            raise ValueError('reference-blueprint is not a connected target-adoption inventory')
        inventory_coverage.update(item['requirement_ids'])
    if not applicable <= inventory_coverage:
        raise ValueError('inventory does not cover applicable requirements with tools or explicit gaps')
    before = snapshot(root, data['capabilities'])
    validate_outputs(root, data, before)
    with tempfile.TemporaryDirectory(prefix='dev-standard-design-') as temporary:
        work = Path(temporary)/'repository'
        shutil.copytree(root, work, symlinks=True, ignore=shutil.ignore_patterns('.git', '__pycache__', '.devflow'))
        # コピー中の変更で誤った対象を検査しない。
        if snapshot(work, data['capabilities']) != before:
            raise ValueError('outputs changed during copy')
        baseline_files = repository_snapshot(work)
        for phase in ('check', 'generate', 'generate'):
            if phase == 'generate':
                # 毎回空から生成し、生成対象から外れた旧fileの残存を防ぐ。
                for cap in data['capabilities'].values():
                    if cap['status'] == 'required':
                        directory = confined(work, cap['output_root'])
                        shutil.rmtree(directory)
                        directory.mkdir(parents=True)
            for cap in data['capabilities'].values():
                if cap['status'] != 'required':
                    continue
                result = subprocess.run(cap[phase], cwd=work, check=False, timeout=300)
                if result.returncode:
                    raise ValueError(f'{phase} command failed ({result.returncode}): {cap[phase]}')
            current = snapshot(work, data['capabilities'])
            if current != before:
                raise ValueError(f'{phase}: drift or nondeterministic generation (byte mismatch)')
            validate_outputs(work, data, current)
            if repository_snapshot(work) != baseline_files:
                raise ValueError(f'{phase}: command changed unowned files or directory/link types')
    if snapshot(root, data['capabilities']) != before:
        raise ValueError('original outputs changed during verification')
    return {'configuration': 'pass', 'design_drift': 'pass', 'execution_tests': {name: read_json(confined(root, cap['report']))['execution_tests'] for name, cap in data['capabilities'].items() if cap['status'] == 'required'}, 'unsupported_surfaces': [], 'files': len(before)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--contract', default='.dev-standard/design.json')
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.root, args.contract), ensure_ascii=False, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'as-built incomplete: {exc}\n')


if __name__ == '__main__':
    main()
