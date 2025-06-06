"""
File Strip.

Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""
import re

LINE_PRESERVE = re.compile(r"\r?\n", re.MULTILINE)

CPP_CODE = r'''
(?P<code>
    "(?:\\.|[^"\\])*"               # double quotes
  | '(?:\\.|[^'\\])*'               # single quotes
  | .[^/"']*                        # everything else
)
'''

PY_CODE = r'''
(?P<code>
    "{3}(?:\\.|[^\\])*"{3}          # triple double quotes
  | '{3}(?:\\.|[^\\])*'{3}          # triple single quotes
  | "(?:\\.|[^"\\])*"               # double quotes
  | '(?:\\.|[^'])*'                 # single quotes
  | .[^\#"']*                       # everything else
)
'''

JSON_CODE = r'''
(?P<code>
    "(?:\\.|[^"\\])*"               # double quotes
  | .[^/"']*                        # everything else
)
'''

CPP_COMMENTS = r'''
(?P<comments>
    /\*[^*]*\*+(?:[^/*][^*]*\*+)*/  # multi-line comments
  | \s*//(?:[^\r\n])*               # single line comments
)
'''

PY_COMMENTS = r'''
(?P<comments>
    \s*\#(?:[^\r\n])*               # single line comments
)
'''

CPP_PATTERN = re.compile(r'(?x)%(comments)s|%(code)s' % {"comments": CPP_COMMENTS, "code": CPP_CODE}, re.DOTALL)

PY_PATTERN = re.compile(r'(?x)%(comments)s|%(code)s' % {"comments": PY_COMMENTS, "code": PY_CODE}, re.DOTALL)

JSON_PATTERN = re.compile(r'(?x)%(comments)s|%(code)s' % {"comments": CPP_COMMENTS, "code": JSON_CODE}, re.DOTALL)


def _strip_regex(pattern, text, preserve_lines):
    """Generic function that strips out comments pased on the given pattern."""

    def remove_comments(group, preserve_lines=False):
        """Remove comments."""

        return ''.join([x[0] for x in LINE_PRESERVE.findall(group)]) if preserve_lines else ''

    def evaluate(m, preserve_lines):
        """Search for comments."""

        g = m.groupdict()
        return g["code"] if g["code"] is not None else remove_comments(g["comments"], preserve_lines)

    return ''.join(map(lambda m: evaluate(m, preserve_lines), pattern.finditer(text)))


@staticmethod
def _cpp(text, preserve_lines=False):
    """C/C++ style comment stripper."""

    return _strip_regex(
        CPP_PATTERN,
        text,
        preserve_lines
    )


@staticmethod
def _json(text, preserve_lines=False):
    """C/C++ style comment stripper."""

    return _strip_regex(
        JSON_PATTERN,
        text,
        preserve_lines
    )


@staticmethod
def _python(text, preserve_lines=False):
    """Python style comment stripper."""

    return _strip_regex(
        PY_PATTERN,
        text,
        preserve_lines
    )


class CommentError(Exception):
    """Comment exception."""

    def __init__(self, value):
        """Setup exception."""

        self.value = value

    def __str__(self):
        """Return exception value repr on string convert."""

        return repr(self.value)


class Comments(object):
    """Comment strip class."""

    styles = []

    def __init__(self, style=None, preserve_lines=False):
        """Initialize."""

        self.preserve_lines = preserve_lines
        self.call = self.__get_style(style)

    @classmethod
    def add_style(cls, style, fn):
        """Add comment style."""

        if style not in cls.__dict__:
            setattr(cls, style, fn)
            cls.styles.append(style)

    def __get_style(self, style):
        """Get the comment style."""

        if style in self.styles:
            return getattr(self, style)
        else:
            raise CommentError(style)

    def strip(self, text):
        """Strip comments."""

        return self.call(text, self.preserve_lines)


Comments.add_style("c", _cpp)
Comments.add_style("json", _json)
Comments.add_style("cpp", _cpp)
Comments.add_style("python", _python)
Comments.add_style("css", _cpp)
