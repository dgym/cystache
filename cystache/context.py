class Context:
    def __init__(self, data, parent = None):
        if isinstance(data, dict):
            self.dict = data
            self.obj = None
        else:
            self.dict = None
            self.obj = data
        self.parent = parent

    def get(self, key):
        if key == '.':
            if self.dict is not None:
                return self.dict
            else:
                return self.obj

        parts = key.split('.')
        key = parts[0]
        ctx = self
        while True:
            if ctx.dict is not None:
                try:
                    value = ctx.dict[key]
                    break
                except:
                    pass
            else:
                try:
                    value = getattr(ctx.obj, key)
                    break
                except:
                    pass

            if ctx.parent:
                ctx = ctx.parent
            else:
                return ''

        for part in parts[1:]:
            try:
                if isinstance(value, dict):
                    value = value[part]
                else:
                    value = getattr(value, part)
            except:
                return ''
        return value or ''
