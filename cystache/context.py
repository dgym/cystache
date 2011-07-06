class Context:
    def __init__(self, data, parent = None):
        self.data = data
        self.is_dict = isinstance(data, dict)
        self.parent = parent

    def get(self, key):
        if key == u'.':
            return self.data

        parts = key.split(u'.')
        key = parts[0]
        ctx = self
        while True:
            if ctx.is_dict:
                try:
                    value = ctx.data[key]
                    break
                except:
                    pass
            else:
                try:
                    value = getattr(ctx.data, key)
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
        return value
