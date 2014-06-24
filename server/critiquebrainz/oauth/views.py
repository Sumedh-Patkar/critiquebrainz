from flask import Blueprint, request, jsonify
from critiquebrainz.oauth import oauth
from critiquebrainz.db import OAuthClient
from critiquebrainz.decorators import nocache
from critiquebrainz.oauth.exceptions import UnsupportedGrantType

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/authorize', methods=['POST'], endpoint='authorize')
@oauth.require_auth('authorization')
@nocache
def oauth_authorize_handler(user):
    """Generate new OAuth grant.

    **OAuth scope:** authorization

    :resheader Content-Type: *application/json*
    """
    client_id = request.form.get('client_id')
    response_type = request.form.get('response_type')
    redirect_uri = request.form.get('redirect_uri')
    scope = request.form.get('scope')

    # validate request
    oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)

    # generate new grant
    code = oauth.generate_grant(client_id, user.id, redirect_uri, scope)

    return jsonify(dict(code=code))


@oauth_bp.route('/token', methods=['POST'], endpoint='token')
@nocache
def oauth_token_handler():
    """OAuth 2.0 token endpoint.

    :form string client_id:
    :form string client_secret:
    :form string redirect_uri:
    :form string grant_type: ``authorization_code`` or ``refresh_token``
    :form string code: (not required if grant_type is ``refresh_token``)
    :form string refresh_token: (not required if grant_type is ``authorization_code``)

    :resheader Content-Type: *application/json*
    """
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    redirect_uri = request.form.get('redirect_uri')
    grant_type = request.form.get('grant_type')
    code = request.form.get('code')
    refresh_token = request.form.get('refresh_token')

    # validate request
    oauth.validate_token_request(grant_type, client_id, client_secret, redirect_uri, code, refresh_token)

    if grant_type == 'authorization_code':
        grant = oauth.fetch_grant(client_id, code)
        user_id = grant.user.id
        scope = grant.scopes
    elif grant_type == 'refresh_token':
        token = oauth.fetch_token(client_id, refresh_token)
        user_id = token.user.id
        scope = token.scopes
    else:
        raise UnsupportedGrantType

    # Deleting grant and/or existing token(s)
    # TODO: Check if that's necessary
    oauth.discard_grant(client_id, code)
    oauth.discard_client_user_tokens(client_id, user_id)

    # generate new token
    access_token, token_type, expires_in, refresh_token = oauth.generate_token(client_id, refresh_token, user_id, scope)

    return jsonify(dict(access_token=access_token,
                        token_type=token_type,
                        expires_in=expires_in,
                        refresh_token=refresh_token))

@oauth_bp.route('/validate', methods=['POST'], endpoint='validate')
@nocache
def oauth_client_handler():
    """Validate OAuth authorization request.

    :form string client_id:
    :form string response_type:
    :form string redirect_uri:
    :form string scope:

    :resheader Content-Type: *application/json*
    """
    client_id = request.form.get('client_id')
    response_type = request.form.get('response_type')
    redirect_uri = request.form.get('redirect_uri')
    scope = request.form.get('scope')

    # validate request
    oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)

    client = OAuthClient.query.get(client_id)

    return jsonify(dict(client=dict(client_id=client.client_id,
                                    name=client.name,
                                    desc=client.desc,
                                    website=client.website)))

