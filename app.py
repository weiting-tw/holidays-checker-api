import argparse
from flask import Flask, request, jsonify
import re
from datetime import datetime
import holidays

app = Flask(__name__)

def validate_date(date_str):
    """Validate the date format YYYY-MM-DD."""
    regex = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(regex, date_str) is not None

@app.route('/isHoliday', methods=['GET'])
def is_holiday():
    date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))  # ex '2025-01-01'
    country = request.args.get('country', 'TW')

    # Validate date format
    if not validate_date(date):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    _holidays = holidays.country_holidays(country, language='TW')

    try:
        is_holiday = date in _holidays
        description = _holidays.get(date)

        return jsonify({
            'country': country,
            'date': date,
            'isHoliday': is_holiday,
            'description': description
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 創建解析器來處理命令行參數
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=5000)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port)
