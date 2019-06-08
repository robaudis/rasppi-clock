from contextlib import contextmanager

class TextScroller:
    def __init__(self, header, text, screenwidth = 20):
        self.header = header
        self.text = text
        self.scrolling = False
        self.slicepos = 0
        self.waitcount = 0
        total_len = len(header) + len(text) + 1
        self.extrachars = total_len - screenwidth if total_len > screenwidth else 0

    @contextmanager
    def scroll(self, scrolldelay = 3, overscroll = 0):
        if self.slicepos > self.extrachars + overscroll:
            self.slicepos = 0
            self.waitcount = 0
            self.scrolling = False

        yield self.header + ' ' + self.text[self.slicepos:]

        self.waitcount += 1
        if self.extrachars and self.waitcount > scrolldelay:
            self.scrolling = True
            self.slicepos += 1
