from flask.views import MethodView
from flask import render_template, request
from services.shared.ServiceAccessManager import ServiceAccessManager, current_participant_client
import json


class ParticipantLocalView(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @ServiceAccessManager.static_token_required
    def get(self):
        # print('get')

        hostname = self.flaskModule.config.service_config['hostname']
        port = self.flaskModule.config.service_config['port']
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']
        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT']

        # Query full participant infos
        # participant_info = current_participant_client.get_participant_infos()

        return render_template('participant_localview.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port)

        # Get participant information
        # response = current_participant_client.do_get_request_to_backend('/api/participant/participants')
        #
        # if response.status_code == 200:
        #     participant_info = response.json()
        #
        #     return render_template('participant.html', hostname=hostname, port=port,
        #                            backend_hostname=backend_hostname, backend_port=backend_port,
        #                            participant_name=participant_info['participant_name'],
        #                            participant_email=participant_info['participant_email'])
        # else:
        #     return 'Unauthorized', 403

