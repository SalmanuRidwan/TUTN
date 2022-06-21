import os

from flask import Flask, jsonify, request, redirect, abort, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime

from functools import wraps
from models import setup_db, CodingSchool, Users

SCHOOLS_PER_PAGE = 3


def paginate_coding_schools(request, coding_schools):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * SCHOOLS_PER_PAGE
    stop = start + SCHOOLS_PER_PAGE

    schools = [school.format() for school in coding_schools]
    current_coding_schools = schools[start:stop]

    return current_coding_schools


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)
    CORS(app)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(32),
        DATABASE=os.path.join(app.instance_path, 'flaskr.postgresql'),
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PUT, POST, DELETE')

        return response

    def token_required(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None

            if 'x-access-tokens' in request.headers:
                token = request.headers['x-access-tokens']

            if not token:
                return jsonify({
                    'message': 'a valid token is missing'
                })

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                current_user = Users.query.filter_by(
                    public_key=data['public_key']).first()
            except:
                return jsonify({
                    'message': 'token is invalid'
                })

            return f(current_user, *args, **kwargs)
        return decorator

    @app.route('/register', methods=['GET', 'POST'])
    def signup_user():
        data = request.get_json()

        hashed_password = generate_password_hash(
            data['password'], method='sha256')
        current_date = datetime.datetime.now()

        try:
            new_user = Users(
                is_admin=False,
                name=data['name'],
                email=data['email'],
                password=hashed_password,
                registered_on=current_date,
                public_key=str(uuid.uuid4()),
            )

            new_user.insert()

            return jsonify({
                'message': 'registered "{}" successfully'.format(new_user.name)
            })
        except:
            abort(422)

    @app.route('/login', methods=['GET', 'POST'])
    def login_user():
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

        user = Users.query.filter_by(name=auth.username).first()

        if check_password_hash(user.password, auth.password):
            token = jwt.encode({'public_key': user.public_key, 'exp': datetime.datetime.now(
            ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

            return jsonify({
                'token': token.decode('UTF-8')
            })

        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    @app.route('/users', methods=['GET'])
    def retrieve_all_users():
        users = Users.query.all()
        result = []

        for user in users:
            user_data = {}
            user_data['is_admin'] = user.is_admin
            user_data['name'] = user.name
            user_data['email'] = user.email
            user_data['password'] = user.password
            user_data['registered_on'] = user.registered_on
            user_data['public_key'] = user.public_key

            result.append(user_data)

        return jsonify({
            'users': result
        })

    @app.route('/codingschools', methods=['POST', 'GET'])
    @token_required
    def create_codingschool(current_user):  # TODO: current user!
        body = request.get_json()

        new_name = body.get('name', None)
        new_address = body.get('address', None)
        new_state = body.get('state', None)
        new_rating = body.get('rating', None)

        try:
            codingschool = CodingSchool(
                name=new_name,
                address=new_address,
                state=new_state,
                rating=new_rating
            )
            codingschool.insert()

            coding_schools = CodingSchool.query.order_by(CodingSchool.id).all()
            current_coding_schools = paginate_coding_schools(
                request, coding_schools)
            all_coding_schools = CodingSchool.query.all()

            return jsonify({
                'success': True,
                'message': 'new coding school created',
                'created': codingschool.id,
                'coding_schools': current_coding_schools,
                'total_coding_schools': len(all_coding_schools)
            })
        except:
            abort(422)

    @app.route('/codingschools', methods=['POST', 'GET'])
    @token_required
    def get_all_codingschools(current_user):
        codingschools = CodingSchool.query.filter_by(
            user_id=current_user.id).all()
        output = []

        for codingschool in codingschools:
            codingschool_data = {}
            codingschool_data['name'] = codingschool.name
            codingschool_data['state'] = codingschool.state
            codingschool_data['address'] = codingschool.address
            codingschool_data['rating'] = codingschool.rating

            output.append(codingschool_data)

        coding_schools = CodingSchool.query.order_by(CodingSchool.id).all()
        current_coding_schools = paginate_coding_schools(
            request, coding_schools)
        return jsonify({
            'success': True,
            'total_coding_schools': len(CodingSchool.query.all()),
            'list of coding schools': output
        })

    @app.route('/codingschools/<int:codingschool_id>', methods=['DELETE'])
    @token_required
    def delete_codingschool(current_user, codingschool_id):
        try:
            codingschool = CodingSchool.query.filter_by(
                id=codingschool_id, user_id=current_user.id).first()

            if codingschool is None:
                abort(404)

            codingschool.delete()
            all_coding_schools = CodingSchool.query.all()

            return jsonify({
                'success': True,
                'message': 'coding school deleted',
                'total_coding_schools': len(all_coding_schools)
            })
        except:
            abort(422)

    '''
    commented out for testing...
    
    '''
    # @app.route('/codingschools')
    # def retrieve_codingschools():
    #     coding_schools = CodingSchool.query.order_by(CodingSchool.id).all()
    #     current_coding_schools = paginate_coding_schools(
    #         request, coding_schools)
    #     return jsonify({
    #         'success': True,
    #         'coding_schools': current_coding_schools,
    #         'total_coding_schools': len(coding_schools)
    #     })

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
