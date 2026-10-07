"""Check almanac JavaScript files and executable inline HTML scripts."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.active = None

    def handle_starttag(self, tag, attrs):
        if tag != 'script':
            return
        attributes = dict(attrs)
        kind = (attributes.get('type') or '').strip().lower()
        executable = kind in ('', 'module', 'text/javascript',
                              'application/javascript', 'text/ecmascript',
                              'application/ecmascript')
        if 'src' not in attributes and executable:
            self.active = [self.getpos()[0], kind == 'module', []]

    def handle_data(self, data):
        if self.active is not None:
            self.active[2].append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.active is not None:
            line, module, pieces = self.active
            self.scripts.append((line, module, ''.join(pieces)))
            self.active = None


def main():
    paths = sorted((ROOT / 'almanac').rglob('*.js'))
    if not paths:
        raise RuntimeError('No almanac JavaScript files found')
    for path in paths:
        subprocess.run(['node', '--check', str(path)], cwd=ROOT, check=True)
    inline_count = 0
    for path in sorted((ROOT / 'almanac').rglob('*.html')):
        parser = InlineScripts()
        parser.feed(path.read_bytes().decode('utf-8'))
        parser.close()
        for line, module, source in parser.scripts:
            command = ['node', '--check', '--input-type=' + ('module' if module else 'commonjs')]
            result = subprocess.run(command, input=source.encode('utf-8'),
                                    cwd=ROOT, capture_output=True)
            if result.returncode:
                raise RuntimeError(f'{path}:{line}: invalid inline JavaScript\n'
                                   + result.stderr.decode('utf-8', errors='replace'))
            inline_count += 1
    print(f'PASS: JavaScript syntax for all {len(paths)} almanac files '
          f'and {inline_count} executable inline scripts')


if __name__ == '__main__':
    main()
