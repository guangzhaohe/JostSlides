"""Local static serving with byte ranges for seeking through presentation videos."""
from email.utils import formatdate
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
import re


class PresentationHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.range_remaining = None
        requested = self.headers.get('Range', '')
        path = Path(self.translate_path(self.path))
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested)
        if not match or not any(match.groups()) or not path.is_file():
            return super().send_head()
        stat = path.stat()
        modified = formatdate(stat.st_mtime, usegmt=True)
        if self.headers.get('If-Range', modified) != modified:
            return super().send_head()
        size = stat.st_size
        first, last = match.groups()
        start = int(first) if first else max(0, size-int(last))
        end = min(int(last), size-1) if first and last else size-1
        if start > end or start >= size:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        stream = path.open('rb')
        stream.seek(start)
        self.range_remaining = end-start+1
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(self.range_remaining))
        self.send_header('Last-Modified', modified)
        self.end_headers()
        return stream

    def copyfile(self, source, outputfile):
        try:
            if self.range_remaining is None:
                return super().copyfile(source, outputfile)
            while self.range_remaining:
                chunk = source.read(min(1024*1024, self.range_remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                self.range_remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Normal when leaving a video slide before its download finishes.
