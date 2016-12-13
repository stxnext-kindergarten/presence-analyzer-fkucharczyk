# -*- coding: utf-8 -*-
"""Defines views."""

import calendar
from flask import redirect, abort, render_template
from jinja2 import TemplateNotFound


from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    group_by_start_end_time,
)

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """Redirects to front page."""
    return redirect('/presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """Users listing for dropdown."""
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """Returns mean presence time of given user grouped by weekday."""
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    return [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """Returns total presence time of given user grouped by weekday."""
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_time(user_id):
    """Returns start and end time of given user grouped by weekday."""
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_start_end_time(data[user_id])
    return [
        (calendar.day_abbr[weekday], start, end)
        for weekday, (start, end) in enumerate(weekdays)
    ]


@app.route('/<string:template_name>')
def render_view(template_name):
    """Render template based on html file."""
    if not template_name.endswith('.html'):
        '{}.html'.format(template_name)
    try:
        return render_template(template_name)
    except TemplateNotFound:
            abort(404)
