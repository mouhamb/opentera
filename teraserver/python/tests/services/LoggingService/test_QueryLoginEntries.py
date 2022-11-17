from BaseLoggingServiceAPITest import BaseLoggingServiceAPITest
from services.LoggingService.libloggingservice.db.models.LoginEntry import LoginEntry
from datetime import datetime, timedelta
import uuid


class LoggingServiceQueryLoginEntriesTest(BaseLoggingServiceAPITest):
    test_endpoint = '/api/logging/login_entries'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with BaseLoggingServiceAPITest.app_context():
            response = self._get_with_service_token_auth(self.test_client, token="invalid")
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_with_invalid_token_but_not_admin(self):
        with BaseLoggingServiceAPITest.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=False, expiration=3600)
            response = self._get_with_service_token_auth(self.test_client, token=token)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_with_valid_token_and_all_enabled_users(self):
        with BaseLoggingServiceAPITest.app_context():
            from services.LoggingService.Globals import service

            # Will get only enabled user uuids
            users = service.get_enabled_users()

            for user in users:
                # Create random login entries
                for i in range(50):
                    entry = LoginEntry()
                    entry.login_timestamp = datetime.now()
                    entry.login_log_level = 1
                    entry.login_sender = 'LoggingServiceQueryLoginEntriesTest'
                    entry.login_user_uuid = user.user_uuid
                    entry.login_participant_uuid = None
                    entry.login_device_uuid = None
                    entry.login_service_uuid = None
                    entry.login_status = 2
                    entry.login_type = 1
                    entry.login_client_ip = '127.0.0.1'
                    entry.login_server_endpoint = '/endpoint'
                    entry.login_client_name = 'client name'
                    entry.login_client_version = 'client version'
                    entry.login_os_name = 'os name'
                    entry.login_os_version = 'os version'
                    entry.login_message = 'random message'
                    LoginEntry.insert(entry)

                token = self._generate_fake_user_token(name=user.user_username, user_uuid=user.user_uuid,
                                                       superadmin=user.user_superadmin, expiration=3600)
                response = self._get_with_service_token_auth(self.test_client, token=token)
                self.assertEqual(response.status_code, 200)

                entries = LoginEntry.get_login_entries_by_user_uuid(user.user_uuid)
                self.assertEqual(len(response.json), len(entries))

                # Delete entries
                for entry in entries:
                    self.assertIsNotNone(entry.id_login_event)
                    LoginEntry.delete(entry.id_login_event)
                    self.assertIsNone(LoginEntry.get_login_entry_by_id(entry.id_login_event))

    def test_get_endpoint_with_valid_token_with_admin_with_start_date_with_end_date(self):
        with BaseLoggingServiceAPITest.app_context():
            from services.LoggingService.Globals import service

            # Will get only enabled user uuids
            users = service.get_enabled_users()
            for user in users:
                current_date = datetime.now()
                yesterday = current_date - timedelta(days=1)
                two_days_ago = current_date - timedelta(days=2)
                a_week_ago = current_date - timedelta(weeks=1)

                def create_entry_with_user_uuid_and_date(entry_uuid: str, entry_date: datetime):
                    entry = LoginEntry()
                    entry.login_timestamp = entry_date
                    entry.login_log_level = 1
                    entry.login_sender = 'LoggingServiceQueryLoginEntriesTest'
                    entry.login_user_uuid = entry_uuid
                    entry.login_participant_uuid = None
                    entry.login_device_uuid = None
                    entry.login_service_uuid = None
                    entry.login_status = 2
                    entry.login_type = 1
                    entry.login_client_ip = '127.0.0.1'
                    entry.login_server_endpoint = '/endpoint'
                    entry.login_client_name = 'client name'
                    entry.login_client_version = 'client version'
                    entry.login_os_name = 'os name'
                    entry.login_os_version = 'os version'
                    entry.login_message = 'random message'
                    return entry

                current_entry = create_entry_with_user_uuid_and_date(user.user_uuid, current_date)
                LoginEntry.insert(current_entry)

                yesterday_entry = create_entry_with_user_uuid_and_date(user.user_uuid, yesterday)
                LoginEntry.insert(yesterday_entry)

                two_days_ago_entry = create_entry_with_user_uuid_and_date(user.user_uuid, two_days_ago)
                LoginEntry.insert(two_days_ago_entry)

                a_week_ago_entry = create_entry_with_user_uuid_and_date(user.user_uuid, a_week_ago)
                LoginEntry.insert(a_week_ago_entry)

                self.assertIsNotNone(current_entry.id_login_event)
                self.assertIsNotNone(yesterday_entry.id_login_event)
                self.assertIsNotNone(two_days_ago_entry.id_login_event)
                self.assertIsNotNone(a_week_ago_entry.id_login_event)

                params = {
                    'start_date': str(a_week_ago.isoformat()),
                    'end_date': str(current_date.isoformat())
                }
                token = self._generate_fake_user_token(name=user.user_username, user_uuid=user.user_uuid,
                                                       superadmin=user.user_superadmin, expiration=3600)

                response = self._get_with_service_token_auth(self.test_client, token=token, params=params)
                self.assertEqual(response.status_code, 200)

                print('a week ago ts', a_week_ago_entry.login_timestamp)
                print('current ts', current_entry.login_timestamp)

                self.assertEqual(len(response.json), 4)

                # Cleanup
                LoginEntry.delete(current_entry.id_login_event)
                LoginEntry.delete(yesterday_entry.id_login_event)
                LoginEntry.delete(two_days_ago_entry.id_login_event)
                LoginEntry.delete(a_week_ago_entry.id_login_event)
