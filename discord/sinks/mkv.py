"""
The MIT License (MIT)

Copyright (c) 2021-present sonicord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import io
import subprocess

from .core import Filters, Sink, default_filters
from .errors import MKVSinkError


class MKVSink(Sink):
    """A special sink for .mkv files.

    .. versionadded:: 2.0
    """

    def __init__(self, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        self.encoding = "mkv"
        self.vc = None
        self.audio_data = {}

    def format_audio(self, audio):
        """Formats the recorded audio.

        Raises
        ------
        MKVSinkError
            Audio may only be formatted after recording is finished.
        MKVSinkError
            Formatting the audio failed.
        """
        if self.vc.recording:
            raise MKVSinkError(
                "Audio may only be formatted after recording is finished."
            )
        args = [
            "ffmpeg",
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-loglevel",
            "error",
            "-ac",
            "2",
            "-i",
            "-",
            "-f",
            "matroska",
            "pipe:1",
        ]
        try:
            process = subprocess.Popen(
                args,  # creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
        except FileNotFoundError:
            raise MKVSinkError("ffmpeg was not found.") from None
        except subprocess.SubprocessError as exc:
            raise MKVSinkError(
                "Popen failed: {0.__class__.__name__}: {0}".format(exc)
            ) from exc

        out = process.communicate(audio.file.read())[0]
        out = io.BytesIO(out)
        out.seek(0)
        audio.file = out
        audio.on_format(self.encoding)
