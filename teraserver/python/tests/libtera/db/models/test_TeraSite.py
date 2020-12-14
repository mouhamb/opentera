import unittest
import os

from sqlalchemy import exc
from libtera.db.Base import db
from modules.DatabaseModule.DBManager import DBManager
from libtera.db.models.TeraSite import TeraSite
from libtera.ConfigManager import ConfigManager


class TeraSiteTest(unittest.TestCase):

    filename = os.path.join(os.path.dirname(__file__), 'TeraSiteTest.db')

    SQLITE = {
        'filename': filename
    }

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.admin_user = None
        self.test_user = None

        self.config = ConfigManager()
        self.config.create_defaults()

        self.db_man = DBManager(self.config)

        self.db_man.open_local(self.SQLITE)

        # Creating default users / tests.
        self.db_man.create_defaults(self.config)

    def tearDown(self):
        pass

    def test_defaults(self):
        pass

    def test_nullable_args(self):
        new_site = TeraSite()
        new_site.site_name = None
        db.session.add(new_site)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()