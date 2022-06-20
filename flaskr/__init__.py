import os

from flask import Flask, jsonify, request, redirect, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from models import setup_db, CodingSchool

SCHOOLS_PER_PAGE = 10


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
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PUT, POST, DELETE')

        return response

    @app.route('/codingschools')
    def retrieve_codingschools():
        coding_schools = CodingSchool.query.order_by(CodingSchool.id).all()
        current_coding_schools = paginate_coding_schools(
            request, coding_schools)
        return jsonify({
            'success': True,
            'coding_schools': current_coding_schools,
            'total_coding_schools': len(coding_schools)
        })

    @app.route('/codingschools/<int:codingschool_id>', methods=['PATCH'])
    def update_codingschool(codingschool_id):
        body = request.get_json()

        try:
            codingschool = CodingSchool.query.filter_by(
                codingschool_id).one_or_none()
            if codingschool is None:
                abort(404)

            if 'rating' in body:
                codingschool.rating = int(body.get('rating'))

            if 'name' in body:
                codingschool.name = body.get('name')

            if 'state' in body:
                codingschool.state = body.get('state')

            if 'address' in body:
                codingschool.address = body.get('address')

            codingschool.update()

            return jsonify({
                'success': True,
                'id': codingschool.id
            })

        except:
            abort(400)

    @app.route('/codingschools', methods=['POST'])
    def create_codingschool():
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
                'created': codingschool.id,
                'coding_schools': current_coding_schools,
                'total_coding_schools': len(all_coding_schools)
            })

        except:
            abort(422)

    @app.route('/codingschools/<int:codingschool_id>', methods=['DELETE'])
    def delete_codingschool(codingschool_id):
        try:
            codingschool = CodingSchool.query.filter(
                CodingSchool.id == codingschool_id).one_or_none()

            if codingschool is None:
                abort(404)

            codingschool.delete()
            coding_schools = CodingSchool.query.order_by(CodingSchool.id).all()
            current_coding_schools = paginate_coding_schools(
                request, coding_schools)
            all_coding_schools = CodingSchool.query.all()

            return jsonify({
                'success': True,
                'deleted': codingschool_id,
                'coding_schools': current_coding_schools,
                'total_coding_schools': len(all_coding_schools)
            })

        except:
            abort(422)

            #############################################################################

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
