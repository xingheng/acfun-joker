
class Entity(object):
    def __init__(self):
        super(Entity, self).__init__()
        self.id = None
        self.title = None
        self.url = None
        self.date = 0
        self.cover = None
        self.channel = None
        self.poster_id = None
        self.poster_name = None
        self.banana = 0
        self.stow = 0
        self.download_url = None

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.id == other.id

    def output(self):
        return u'''\
    ID: {}
    Title: {}
    Channel: {}
    User: {}
    Banana: {}
    Stow: {}
    Download: {}'''\
    .format(self.id, self.title, self.channel, self.poster_name, self.banana, self.stow, self.download_url)
