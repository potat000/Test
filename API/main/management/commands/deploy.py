from Iuno.deploy import Command as _Command

class Command(_Command):

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
