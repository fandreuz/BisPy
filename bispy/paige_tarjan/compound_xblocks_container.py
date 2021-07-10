class CompoundXBlocksContainer:
    def __init__(self, xblocks):
        self._xblocks = xblocks

    def pop(self):
        return self._xblocks.pop()

    def append(self, xblock):
        self._xblocks.append(xblock)

    def extend(self, xblocks):
        self._xblocks.extend(xblocks)

    def __len__(self):
        return len(self._xblocks)
