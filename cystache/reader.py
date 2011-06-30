class Reader:
    def __init__(self, source, start = 0, end = -1):
        self.source = source
        self.start = start
        self.end = end

        if self.end == -1:
            self.end = len(self.source)

        # idx is the curront position
        self.idx = start

        # tag positions
        self.tag_start = -1
        self.tag_inner_start = -1
        self.tag_inner_end = -1
        self.tag_end = -1

        self._is_standalone = False
        self._standalone_scanned = True
        self._indent_length = -2
        self._trailing_whitespace_length = -2

        self.static_start = self.idx
        self.static_on_newline = True

    def get_start_idx(self):
        # skip trailing whitespace
        if self._is_standalone:
            self.idx += self.get_trailing_whitespace_length()
            self.static_on_newline = True
        else:
            self.static_on_newline = self.idx == self.start

        self.static_start = self.idx
        return self.idx

    def find_opening_tag(self, otag):
        # reset the standalone scan
        self._standalone_scanned = False
        self._indent_length = -2
        self._trailing_whitespace_length = -2

        self.tag_start = self.source.find(otag, self.idx, self.end)
        if self.tag_start == -1:
            self.tag_start = self.end
            return False
        
        self.tag_inner_start = self.tag_start + len(otag)
        if self.tag_inner_start >= self.end:
            return False
        
        self.idx = self.tag_inner_start
        return True

    def skip_over(self, token):
        self.idx = self.source.find(token, self.tag_inner_start, self.end)
        if self.idx != -1:
            self.idx += 1
        return self.idx

    def find_closing_tag(self, ctag):
        self.tag_inner_end = self.source.find(ctag, self.idx, self.end)
        if self.tag_inner_end == -1:
            return False

        self.tag_end = self.tag_inner_end + len(ctag)
        self.idx = self.tag_end
        return True

    def get_tag(self, slice_start = 0, slice_end = -1):
        return self.source[self.tag_inner_start:self.tag_inner_end][slice_start:slice_end].strip()

    def never_standalone(self):
        self._standalone_scanned = True
        self._is_standalone = False

    def is_standalone(self):
        if not self._standalone_scanned:
            self._standalone_scanned = True
            self._is_standalone = self.get_indent_length() != -1 and \
                self.get_trailing_whitespace_length() != -1
        return self._is_standalone

    def get_indent_length(self):
        if self._indent_length == -2:
            self._indent_length = 0
            for i in range(self.tag_start-1, self.start-1, -1):
                c = self.source[i]
                if c == u'\r' or c == u'\n':
                    break
                elif c != u' ' and c != u'\t':
                    self._indent_length = -1
                    break
                self._indent_length += 1
        return self._indent_length

    def get_indent(self):
        if self.is_standalone():
            l = self.get_indent_length()
            if l > 0:
                return self.source[self.tag_start-l:self.tag_start]
        return u''

    def get_trailing_whitespace_length(self):
        if self._trailing_whitespace_length == -2:
            self._trailing_whitespace_length = 0
            for i in range(self.tag_end, self.end):
                c = self.source[i]
                if c == u'\r':
                    if i + 1 < self.end and self.source[i + 1] == '\n':
                        self._trailing_whitespace_length += 2
                    else:
                        self._trailing_whitespace_length += 1
                    break
                if c == u'\n':
                    self._trailing_whitespace_length += 1
                    break
                elif c != u' ' and c != u'\t':
                    self._trailing_whitespace_length = -1
                    break
                self._trailing_whitespace_length += 1
        return self._trailing_whitespace_length
