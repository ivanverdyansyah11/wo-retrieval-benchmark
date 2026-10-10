"""Local researcher annotation / export / gated pooled development evaluation CLI."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
import sys
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from wo_retrieval import human_judgments as judgments
from wo_retrieval import human_metrics as metrics


def export(package, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    records = judgments.current_records(package)
    judgments.atomic_text(out / 'human_judgments.jsonl', judgments.jsonl_text(records))
    resolved = [r for r in records if r['status'] == 'RESOLVED']
    trec = ''.join(f"{r['binding']['query_id']}\t0\t{r['binding']['chunk_id']}\t{r['grade']}\n"
                   for r in sorted(resolved, key=lambda r: (r['binding']['query_id'], r['binding']['chunk_id'])))
    judgments.atomic_text(out / 'human_resolved_qrels.tsv', trec)
    judgments.write_json(out / 'export_manifest.json', dict(label=judgments.LABEL, scope='development',
        expert_validated=False, independently_validated=False, completeness=judgments.completeness(package, records),
        package_id=package['manifest']['package_id'], input_sha256=package['manifest']['input_sha256'],
        protocol_sha256=package['manifest']['protocol_sha256'],
        history_sha256=judgments.file_hash(package['workspace'] / 'human_judgment_history.jsonl'),
        outputs={p.name: judgments.file_hash(p) for p in sorted(out.iterdir())},
        warning='TSV contains only RESOLVED pairs; absent pairs remain unknown, not Grade 0.'))


def make_server(package, port):
    token = secrets.token_urlsafe(32)
    html = (ROOT / 'src/wo_retrieval/human_annotation.html').read_text(encoding='utf-8').replace('__TOKEN__', json.dumps(token))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, code, data, content_type='application/json; charset=utf-8', attachment=False):
            body = data.encode('utf-8') if isinstance(data, str) else json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'")
            if attachment:
                self.send_header('Content-Disposition', 'attachment; filename="human_judgments_development.jsonl"')
            self.end_headers(); self.wfile.write(body)

        def local_request(self):
            hosts = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            return (self.headers.get('Host') in hosts
                    and (self.headers.get('Origin') is None or self.headers.get('Origin') in {'http://' + h for h in hosts}))

        def do_GET(self):
            if not self.local_request():
                self.reply(403, {'error': 'Hanya browser lokal diizinkan.'}); return
            parsed = urlparse(self.path)
            if parsed.path == '/':
                self.reply(200, html, 'text/html; charset=utf-8'); return
            try:
                records = judgments.current_records(package)
                if parsed.path == '/api/export':
                    self.reply(200, judgments.jsonl_text(records), 'application/x-ndjson; charset=utf-8', True); return
                if parsed.path != '/api/state':
                    self.reply(404, {'error': 'Tidak ditemukan.'}); return
                params = parse_qs(parsed.query)
                wanted = params.get('filter', [None])[0]
                if wanted not in (None, 'PENDING', 'UNRESOLVED'):
                    raise ValueError('Filter tidak valid.')
                if wanted:
                    index = next((i for i, r in enumerate(records) if r['status'] == wanted), None)
                    if index is None:
                        raise ValueError('Tidak ada pasangan dengan status tersebut.')
                elif 'index' in params:
                    index = int(params['index'][0])
                else:
                    index = next((i for i, r in enumerate(records) if r['status'] == 'PENDING'), 0)
                if not 0 <= index < len(records):
                    raise ValueError('Posisi di luar jumlah pasangan.')
                r = records[index]
                self.reply(200, dict(index=index, pair=package['rows'][index],
                    judgment={k: r[k] for k in ('status','grade','notes','evidence','revision')},
                    progress=judgments.completeness(package, records)))
            except (ValueError, KeyError, OSError) as error:
                self.reply(400, {'error': str(error)})

        def do_POST(self):
            if not self.local_request() or self.path != '/api/save':
                self.reply(403, {'error': 'Permintaan lokal tidak valid.'}); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 100000 or self.headers.get('Content-Type') != 'application/json':
                    raise ValueError('Ukuran/format permintaan tidak valid.')
                value = json.loads(self.rfile.read(length))
                if set(value) != {'token','assessment_id','status','grade','notes','evidence','expected_revision'}:
                    raise ValueError('Field permintaan tidak valid.')
                if not isinstance(value['token'], str) or not secrets.compare_digest(value.pop('token'), token):
                    self.reply(403, {'error': 'Token sesi tidak valid; muat ulang tab.'}); return
                # A request can choose a grade; it cannot replace source text, provenance or snapshot bindings.
                event = judgments.save_decision(package, **value)
                self.reply(200, dict(judgment={k: event[k] for k in ('status','grade','notes','evidence','revision')},
                    progress=judgments.completeness(package, judgments.current_records(package))))
            except (ValueError, KeyError, TypeError, OSError) as error:
                self.reply(400, {'error': str(error)})

    return HTTPServer(('127.0.0.1', port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=ROOT / judgments.WORKSPACE)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('prepare', help='Create an empty development human workspace; never overwrite')
    serve = commands.add_parser('serve', help='Local browser annotation, bind 127.0.0.1 only')
    serve.add_argument('--port', type=int, default=8765)
    commands.add_parser('status', help='Completeness only; no effectiveness metrics')
    exp = commands.add_parser('export', help='Export current human-only judgments into a new directory')
    exp.add_argument('--out', required=True, type=Path)
    ev = commands.add_parser('evaluate', help='Gated pooled DEVELOPMENT evaluation; main disabled')
    ev.add_argument('--out', required=True, type=Path)
    ev.add_argument('--word', action='store_true', help='Word report only if all gates pass')
    args = parser.parse_args(argv)
    try:
        if args.command == 'prepare':
            package = judgments.prepare(ROOT, args.workspace)
        else:
            package = judgments.load_package(ROOT, args.workspace)
        if args.command == 'serve':
            with judgments.exclusive(package['workspace'] / '.server.lock'):
                server = make_server(package, args.port)
                print(f'Buka http://127.0.0.1:{server.server_port} — Ctrl+C untuk berhenti.', flush=True)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    pass
                finally:
                    server.server_close()
            return 0
        if args.command in ('prepare', 'status'):
            print(json.dumps(judgments.completeness(package, judgments.current_records(package)), ensure_ascii=False, indent=2))
        elif args.command == 'export':
            if not args.out.resolve().is_relative_to(package['workspace'] / 'exports'):
                raise ValueError('Export must use a new folder below workspace/exports')
            export(package, args.out)
        elif args.command == 'evaluate':
            if not args.out.resolve().is_relative_to(ROOT / 'experiments/results/human_development_evaluation'):
                raise ValueError('Evaluation output must be a new dedicated human_development_evaluation folder')
            rankings = judgments.read_jsonl(ROOT / package['manifest']['ranking_path'])
            result = metrics.evaluate(package, judgments.current_records(package), rankings)
            if args.word and result['status'] != 'VALID_COMPLETED_DEVELOPMENT_POOLED':
                raise ValueError('Human judgments incomplete/zero ideal; Word metrics report not created')
            metrics.publish_report(result, args.out)
            if args.word:
                metrics.write_word(result, args.out / 'development_metrics_report.docx')
            print(result['status'])
            return 0 if result['status'] == 'VALID_COMPLETED_DEVELOPMENT_POOLED' else 2
        return 0
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
