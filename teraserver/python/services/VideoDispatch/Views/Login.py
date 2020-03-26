from flask.views import MethodView
from flask import render_template, request, redirect
from services.VideoDispatch.Globals import ParticipantTokenCookieName


class Login(MethodView):
    # Decorators everywhere?
    # decorators = [auth.login_required]

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    def get(self):
        # Participant login
        if 'participant_token' in request.args:
            # Create cookie
            # path = '/participant'
            path = '/dashboard'

            if 'X-Script-Name' in request.headers:
                path = request.headers['X-Script-Name'] + path

            # redirect to  participant dashboard, will verify login information..
            # response = redirect(path + '?participant_token=' + request.args['participant_token'])
            response = redirect(path)

            # Set cookie
            response.set_cookie(ParticipantTokenCookieName, request.args['participant_token'], 30)

            return response
        else:
            hostname = self.flaskModule.config.server_config['hostname']
            port = self.flaskModule.config.server_config['port']
            backend_hostname = self.flaskModule.config.backend_config['hostname']
            backend_port = self.flaskModule.config.backend_config['port']
            if 'X-Externalhost' in request.headers:
                backend_hostname = request.headers['X-Externalhost']

            if 'X-Externalport' in request.headers:
                backend_port = request.headers['X-Externalport']

            # Render page
            return render_template('login.html', hostname=hostname, port=port,
                                   backend_hostname=backend_hostname, backend_port=backend_port)

    def post(self):
        print('post')
        pass