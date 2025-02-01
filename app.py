import argparse
from flask import Flask, request, jsonify
import re
from datetime import datetime
import holidays
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

def validate_date(date_str):
    """Validate the date format YYYY-MM-DD."""
    regex = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(regex, date_str) is not None

def find_makeup_date(date_object, holidays_items):
    """Check for the makeup workday based on holiday descriptions."""
    for holiday_date, desc in holidays_items:
        if "休息日" in desc:
            pattern = r'(\d{4}-\d{2}-\d{2})'
            matches = re.findall(pattern, desc)
            if matches:
                for match in matches:
                    if match == date_object.strftime('%Y-%m-%d'):
                        return holiday_date
    return None

@app.route('/isHoliday', methods=['GET'])
def is_holiday():
    """Check if the specified date is a holiday or a makeup workday."""
    date_arg = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))  # ex '2025-01-01'
    country = request.args.get('country', 'TW')

    # Validate date format
    if not validate_date(date_arg):
        logging.warning(f'Invalid date format requested: {date_arg}')
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    _holidays = holidays.country_holidays(country, language='TW', years=int(date_arg.split('-')[0]))
    date = datetime.strptime(date_arg, '%Y-%m-%d').date()
    is_holiday = date in _holidays
    holiday_description = _holidays.get(date)

    response = {
        'country': country,
        'date': date_arg,
        'isHoliday': is_holiday,
        'isWorkday': bool(not is_holiday),
        'description': holiday_description if is_holiday else '工作日'
    }

    is_weekend = date.weekday() in [5, 6]
    if is_weekend:
        makeup_workday = find_makeup_date(date, _holidays.items())
        response['isHoliday'] = True
        response['isWorkday'] = False
        response['description'] = f'週末'
        if makeup_workday:
            response['isHoliday'] = False
            response['isWorkday'] = True
            response['description'] = f'{makeup_workday.strftime("%Y-%m-%d")} 的補班日'

    return jsonify(response)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=5000)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port)
