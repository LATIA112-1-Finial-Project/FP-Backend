import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response, jsonify
)

from flaskr.db import get_db
from flask_argon2 import Argon2
from flaskr.models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS, cross_origin
from flaskr.models.TopUni.academic_reputation import Academic
from flaskr.models.TopUni.employer_reputation import Employer
from flaskr.models.TopUni.overall import Overall
from flaskr.models.TopUni.university_id_name import University

bp_top_uni = Blueprint('bp_top_uni', __name__, url_prefix='/api/v1/auth')

CORS(bp_top_uni, resources={r"/*": {"origins": "*"}})


@bp_top_uni.route('/university_attr/<int:university_id>', methods=['GET'])
@jwt_required()
def university_attr(university_id):
    # Get the id from the request body

    if university_id is None:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'request id error'
        }), 400)
    if university_id < 1 or university_id > 1147:
        return make_response(jsonify({
            'code': 400,
            'msg': 'error',
            'data': 'request id error'
        }), 400)

    id_to_query = university_id

    db = get_db()
    # Query the database to get the information
    # use id_to_query to get university name from University table, type is string
    # use id_to_query to get academic reputation rank, score, year from Academic table

    university_name = db.query(University.name).filter(University.id == id_to_query).first()
    university_name = university_name[0]

    # Get academic reputation information
    academic_reputation_info_rank_list = []
    academic_reputation_info_score_list = []
    academic_reputation_info_year_list = []
    # id_to_query can be found many times in Academic table, so we need to use for loop to get all the information
    for academic_reputation_info in db.query(Academic.ar_rank, Academic.ar_score, Academic.ar_year).filter(
            Academic.university_id == id_to_query).all():
        academic_reputation_info_rank_list.append(academic_reputation_info.ar_rank)
        academic_reputation_info_score_list.append(academic_reputation_info.ar_score)
        academic_reputation_info_year_list.append(academic_reputation_info.ar_year)

    # Get employer reputation information
    employer_reputation_info_rank_list = []
    employer_reputation_info_score_list = []
    employer_reputation_info_year_list = []
    # id_to_query can be found many times in Employer table, so we need to use for loop to get all the information
    for employer_reputation_info in db.query(Employer.er_rank, Employer.er_score, Employer.er_year).filter(
            Employer.university_id == id_to_query).all():
        employer_reputation_info_rank_list.append(employer_reputation_info.er_rank)
        employer_reputation_info_score_list.append(employer_reputation_info.er_score)
        employer_reputation_info_year_list.append(employer_reputation_info.er_year)

    # Get overall information
    overall_info_rank_list = []
    overall_info_score_list = []
    overall_info_year_list = []
    # id_to_query can be found many times in Overall table, so we need to use for loop to get all the information
    for overall_info in db.query(Overall.o_rank, Overall.o_score, Overall.o_year).filter(
            Overall.university_id == id_to_query).all():
        overall_info_rank_list.append(overall_info.o_rank)
        overall_info_score_list.append(overall_info.o_score)
        overall_info_year_list.append(overall_info.o_year)

    response_data = jsonify({
        'code': 200,
        'msg': 'success',
        'data': {
            'university_name': university_name,
            'academic_reputation_info_rank_list': academic_reputation_info_rank_list,
            'academic_reputation_info_score_list': academic_reputation_info_score_list,
            'academic_reputation_info_year_list': academic_reputation_info_year_list,
            'employer_reputation_info_rank_list': employer_reputation_info_rank_list,
            'employer_reputation_info_score_list': employer_reputation_info_score_list,
            'employer_reputation_info_year_list': employer_reputation_info_year_list,
            'overall_info_rank_list': overall_info_rank_list,
            'overall_info_score_list': overall_info_score_list,
            'overall_info_year_list': overall_info_year_list
        }
    })

    return response_data, 200
