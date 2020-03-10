from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraDeviceType import TeraDeviceType
from libtera.db.models.TeraServerSettings import TeraServerSettings

import uuid
import jwt
import time
import datetime


class TeraDevice(db.Model, BaseModel):
    __tablename__ = 't_devices'
    secret = None
    id_device = db.Column(db.Integer, db.Sequence('id_device_sequence'), primary_key=True, autoincrement=True)
    # id_site = db.Column(db.Integer, db.ForeignKey("t_sites.id_site", ondelete='cascade'), nullable=True)
    # id_session_type = db.Column(db.Integer, db.ForeignKey("t_sessions_types.id_session_type",
    #                                                       ondelete='set null'), nullable=True)
    device_uuid = db.Column(db.String(36), nullable=False, unique=True)
    device_name = db.Column(db.String, nullable=False)
    device_type = db.Column(db.Integer, db.ForeignKey('t_devices_types.id_device_type', ondelete='cascade'),
                            nullable=False)
    id_device_subtype = db.Column(db.Integer, db.ForeignKey('t_devices_subtypes.id_device_subtype',
                                                            ondelete='set null'), nullable=True)
    device_token = db.Column(db.String, nullable=False, unique=True)
    device_certificate = db.Column(db.String, nullable=True)
    device_enabled = db.Column(db.Boolean, nullable=False, default=False)
    device_onlineable = db.Column(db.Boolean, nullable=False, default=False)
    device_optional = db.Column(db.Boolean, nullable=False, default=False)
    device_config = db.Column(db.String, nullable=True)
    device_infos = db.Column(db.String, nullable=True)
    device_notes = db.Column(db.String, nullable=True)
    device_lastonline = db.Column(db.TIMESTAMP, nullable=True)

    # device_sites = db.relationship("TeraDeviceSite")
    device_projects = db.relationship('TeraDeviceProject')
    # device_session_types = db.relationship("TeraSessionTypeDeviceType")
    device_participants = db.relationship("TeraParticipant",  secondary="t_devices_participants",
                                          back_populates="participant_devices")
    device_subtype = db.relationship('TeraDeviceSubType')

    authenticated = False

    def __init__(self):
        self.secret = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerDeviceTokenKey)
        if self.secret is None:
            # Fallback - should not happen
            self.secret = 'TeraDeviceSecret'

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields += ['device_projects', 'device_participants', 'device_certificate', 'secret',
                          'device_subtype', 'authenticated']

        if minimal:
            ignore_fields += ['device_type', 'device_uuid', 'device_onlineable', 'device_config', 'device_notes',
                              'device_lastonline', 'device_infos',  'device_token']

        device_json = super().to_json(ignore_fields=ignore_fields)

        return device_json

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def is_active(self):
        return self.device_enabled

    def get_id(self):
        return self.device_uuid

    def is_login_enabled(self):
        return self.device_onlineable

    def create_token(self):
        # Creating token with user info
        payload = {
            'iat': int(time.time()),
            'device_uuid': self.device_uuid,
            'device_name': self.device_name,
            'device_type': self.device_type
        }

        self.device_token = jwt.encode(payload, TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerDeviceTokenKey), algorithm='HS256').decode('utf-8')

        return self.device_token

    def update_last_online(self):
        self.device_lastonline = datetime.datetime.now()
        db.session.commit()

    @staticmethod
    def get_device_by_token(token):
        device = TeraDevice.query.filter_by(device_token=token).first()

        if device:
            # Validate token, key loaded from DB
            data = jwt.decode(token.encode('utf-8'),
                              TeraServerSettings.get_server_setting_value(
                                  TeraServerSettings.ServerDeviceTokenKey), algorithms='HS256')

            # Only validating UUID since other fields can change in database after token is generated.
            if data['device_uuid'] == device.device_uuid:

                # Update last online
                device.update_last_online()
                device.authenticated = True
                return device
            else:
                return None

        return None

    @staticmethod
    def get_device_by_uuid(dev_uuid):
        device = TeraDevice.query.filter_by(device_uuid=dev_uuid).first()
        if device:
            device.update_last_online()
            return device

        return None

    @staticmethod
    def get_device_by_name(name):
        return TeraDevice.query.filter_by(device_name=name).first()

    @staticmethod
    def get_device_by_id(device_id):
        return TeraDevice.query.filter_by(id_device=device_id).first()

    @staticmethod
    # Available device = device not assigned to any participant
    def get_available_devices(ignore_disabled=True):
        if ignore_disabled:
            return TeraDevice.query.outerjoin(TeraDevice.device_participants)\
                .filter(TeraDevice.device_participants == None).all()
        else:
            return TeraDevice.query.filter_by(device_enabled=True).outerjoin(TeraDevice.device_participants).\
                filter(TeraDevice.device_participants == None).all()

    @staticmethod
    # Unvailable device = device assigned to at least one participant
    def get_unavailable_devices(ignore_disabled=True):
        if ignore_disabled:
            return TeraDevice.query.join(TeraDevice.device_participants).all()
        else:
            return TeraDevice.query.filter_by(device_enabled=True).join(TeraDevice.device_participants).all()

    @staticmethod
    def create_defaults():
        device = TeraDevice()
        device.device_name = 'Apple Watch #W05P1'
        # Forcing uuid for tests
        device.device_uuid = 'b707e0b2-e649-47e7-a938-2b949c423f73'  # str(uuid.uuid4())
        device.device_type = TeraDeviceType.DeviceTypeEnum.SENSOR.value
        device.create_token()
        device.device_enabled = True
        device.device_onlineable = True
        # device.device_site = TeraSite.get_site_by_sitename('Default Site')
        # device.device_participants = [TeraParticipant.get_participant_by_id(1)]
        db.session.add(device)

        device2 = TeraDevice()
        device2.device_name = 'Kit Télé #1'
        device2.device_uuid = str(uuid.uuid4())
        device2.device_type = TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value
        device2.create_token()
        device2.device_enabled = True
        device2.device_onlineable = True
        # device2.device_sites = [TeraSite.get_site_by_sitename('Default Site')]
        # device2.device_participants = [TeraParticipant.get_participant_by_id(1),
        #                               TeraParticipant.get_participant_by_id(2)]
        db.session.add(device2)

        device3 = TeraDevice()
        device3.device_name = 'Robot A'
        device3.device_uuid = str(uuid.uuid4())
        device3.device_type = TeraDeviceType.DeviceTypeEnum.ROBOT.value
        device3.create_token()
        device3.device_enabled = True
        device3.device_onlineable = True
        # device3.device_sites = [TeraSite.get_site_by_sitename('Default Site')]
        # device3.device_participants = [TeraParticipant.get_participant_by_id(2)]
        db.session.add(device3)

        db.session.commit()

    @classmethod
    def insert(cls, device):
        # Generate UUID
        device.device_uuid = str(uuid.uuid4())

        # Clear last online field
        device.device_lastonline = None

        # Create token
        device.create_token()

        super().insert(device)

    @classmethod
    def delete(cls, id_todel):
        super().delete(id_todel)

        from libtera.db.models.TeraDeviceData import TeraDeviceData
        TeraDeviceData.delete_files_for_device(id_todel)
