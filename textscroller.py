from contextlib import contextmanager

class TextScroller:
    def __init__(self, text, screenwidth = 20):
        self.text = text
        self.scrolling = False
        self.slicepos = 0
        self.waitcount = 0
        self.extrachars = len(text) - screenwidth if len(text) > screenwidth else 0

    @contextmanager
    def scroll(self, scrolldelay = 3, overscroll = 0):
        if self.slicepos > self.extrachars + overscroll:
            self.slicepos = 0
            self.waitcount = 0
            self.scrolling = False

        yield self.text[self.slicepos:]

        self.waitcount += 1
        if self.extrachars and self.waitcount > scrolldelay:
            self.scrolling = True
            self.slicepos += 1
