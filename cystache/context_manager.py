class ContextManager:
    def __init__(self):
        self.context = None
        self.template = None
        self.thread_storage = None

    def enable_threading(self):
        if self.thread_storage:
            return
        import threading
        self.thread_storage = threading.local()
        self.thread_storage.context = self.context
        self.thread_storage.template = self.template

    def get_current_context(self):
        if self.thread_storage:
            return self.thread_storage.context
        return self.context

    def get_current_template(self):
        if self.thread_storage:
            return self.thread_storage.template
        return self.template

    def _set_current_context(self, context):
        if self.thread_storage:
            old = self.thread_storage.context
            self.thread_storage.context = context
            return old
        old = self.context
        self.context = context
        return old

    def _set_current_template(self, template):
        if self.thread_storage:
            old = self.thread_storage.template
            self.thread_storage.template = template
            return old
        old = self.template
        self.template = template
        return old


context_manager = ContextManager()
