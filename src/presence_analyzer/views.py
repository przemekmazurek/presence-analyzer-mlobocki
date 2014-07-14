# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, render_template, url_for

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    additional_data,
    mean,
    group_by_weekday,
    start_end_presence,
)

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('render_weekday'))


@app.route('/mean_time_weekday.html')
def render_mean_time():
    """
    Renders mean time view.
    """
    return render_template('mean_time_weekday.html')


@app.route('/presence_start_end.html')
def render_start_end():
    """
    Renders presence start/end.
    """
    return render_template('presence_start_end.html')


@app.route('/presence_weekday.html')
def render_weekday():
    """
    Renders presence start/end.
    """
    return render_template('presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = additional_data()
    return data


@app.route('/api/v1/mean_time_weekday/', methods=['GET'])
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/', methods=['GET'])
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end_view/', methods=['GET'])
@app.route('/api/v1/presence_start_end_view/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns presence start/end view.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = start_end_presence(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(time['start']), mean(time['end']))
        for weekday, time in weekdays.items()
    ]
    return result
