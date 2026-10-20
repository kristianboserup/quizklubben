"""Quizklubben: local server with atomic JSON persistence. Python 3.9+."""
import argparse
import json
import os
from pathlib import Path
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import webbrowser

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'quiz-state.json'
LOCK = threading.Lock()
MAX_BYTES = 8 * 1024 * 1024


def validate_document(document):
    if not isinstance(document, dict):
        raise ValueError('Ugyldigt dokument')
    quiz = document.get('quiz')
    if not isinstance(quiz, dict) or quiz.get('version') != 1:
        raise ValueError('Ugyldig quiz')
    if not isinstance(quiz.get('players'), list) or not isinstance(quiz.get('rounds'), list):
        raise ValueError('Manglende deltagere eller runder')
    if not isinstance(document.get('responses'), dict):
        raise ValueError('Ugyldige svar')
    return document


def read_document():
    if not DATA.exists():
        return None
    document = validate_document(json.loads(DATA.read_text(encoding='utf-8')))
    if type(document.get('revision')) is not int or document['revision'] < 1:
        raise ValueError('Ugyldig filversion')
    return document


def atomic_write(document):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    temp = DATA.with_suffix('.tmp')
    try:
        with temp.open('w', encoding='utf-8', newline='\n') as stream:
            json.dump(document, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, DATA)
    finally:
        if temp.exists():
            temp.unlink()


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload, content_type='application/json; charset=utf-8'):
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def local_request(self):
        expected = 'http://127.0.0.1:' + str(self.server.server_port)
        return self.headers.get('Host') == expected.removeprefix('http://') and self.headers.get('Origin', expected) == expected

    def do_GET(self):
        if not self.local_request():
            return self.reply(403, {'error': 'Kun lokal adgang'})
        if self.path == '/api/state':
            try:
                with LOCK:
                    document = read_document()
                return self.reply(200, document or {'revision': 0, 'quiz': None, 'responses': {}})
            except (ValueError, OSError) as error:
                print('Kunne ikke indlaese data:', error)
                return self.reply(500, {'error': 'JSON-filen kunne ikke læses. Den er bevaret uændret.'})
        if self.path in ('/', '/quiz.html'):
            try:
                return self.reply(200, (ROOT / 'quiz.html').read_bytes(), 'text/html; charset=utf-8')
            except OSError:
                return self.reply(500, {'error': 'quiz.html mangler i serverens mappe'})
        if self.path == '/favicon.ico':
            return self.reply(204, b'', 'image/x-icon')
        return self.reply(404, {'error': 'Siden findes ikke'})

    def do_PUT(self):
        if self.path != '/api/state':
            return self.reply(404, {'error': 'Siden findes ikke'})
        if not self.local_request() or self.headers.get('X-Quizklubben') != '1':
            return self.reply(403, {'error': 'Kun lokal adgang'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.reply(415, {'error': 'JSON kræves'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BYTES:
                return self.reply(413, {'error': 'Filen er tom eller større end 8 MB'})
            incoming = validate_document(json.loads(self.rfile.read(length).decode('utf-8')))
            revision = incoming.get('revision')
            if type(revision) is not int or revision < 0:
                raise ValueError('Ugyldig filversion')
            with LOCK:
                previous = read_document()
                if revision != (previous['revision'] if previous else 0):
                    return self.reply(409, {'error': 'Quizzen er ændret i en anden fane. Hent en sikkerhedskopi af dine ændringer, og genindlæs siden.'})
                document = {'revision': revision + 1, 'quiz': incoming['quiz'], 'responses': incoming['responses']}
                atomic_write(document)
            return self.reply(200, {'revision': document['revision']})
        except (ValueError, UnicodeError):
            return self.reply(400, {'error': 'Ugyldig JSON eller quizdata'})
        except OSError as error:
            print('Kunne ikke gemme data:', error)
            return self.reply(500, {'error': 'Kunne ikke skrive JSON-filen på disken'})


def main():
    parser = argparse.ArgumentParser(description='Start Quizklubben lokalt')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    except OSError as error:
        print('Serveren kunne ikke starte. Er Quizklubben allerede startet?')
        print(error)
        return 1
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Quizklubben koerer paa {url}')
    print(f'Resultater gemmes i: {DATA}')
    print('Lad vinduet vaere aabent. Stop med Ctrl+C, naar siden viser: Gemt i JSON-fil.')
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nQuizklubben er stoppet.')
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
