from flask import Flask, render_template,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime,timedelta
import json
app = Flask(__name__)
application = app
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/blacklight'  
db = SQLAlchemy(app)

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)




with app.app_context():
            db.create_all()

@app.route('/')
def home():
   
    return 'Hello Welcome To Blacklight Assignment by Pradeep Saini'
def get_current_week_leaderboard():
    end_date = datetime.utcnow() - timedelta(days=(datetime.utcnow().weekday() + 1) % 7)
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    start_date = end_date - timedelta(days=6, hours=end_date.hour, minutes=end_date.minute, seconds=end_date.second, microseconds=end_date.microsecond)
    

    leaderboard = User.query.filter(User.timestamp.between(start_date, end_date)) \
                           .order_by(User.score.desc()).limit(200).all()
    result = [{'uid': user.uid, 'name': user.name, 'score': user.score, 'country': user.country} for user in leaderboard]
    return result

def get_last_week_leaderboard_by_country(country_code):
    end_date = datetime.utcnow() - timedelta(days=(datetime.utcnow().weekday() + 1) % 7)
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    start_date = end_date - timedelta(days=6, hours=end_date.hour, minutes=end_date.minute, seconds=end_date.second, microseconds=end_date.microsecond)
    
    leaderboard = User.query.filter(User.timestamp.between(start_date, end_date),
                                    User.country == country_code) \
                           .order_by(desc(User.score)).limit(200).all()

    result = [{'uid': user.uid, 'name': user.name, 'score': user.score, 'country': user.country} for user in leaderboard]
    return result

def get_user_rank(user_id):
    user = User.query.filter_by(uid=user_id).first()
    if user:
        end_date = datetime.utcnow() - timedelta(days=(datetime.utcnow().weekday() + 1) % 7)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        start_date = end_date - timedelta(days=6, hours=end_date.hour, minutes=end_date.minute, seconds=end_date.second, microseconds=end_date.microsecond)
    
        rank = User.query.filter(User.timestamp.between(start_date, end_date),
                                 User.score > user.score).count() + 1
        return rank
    else:
        return None

# API 1: Display current week leaderboard (Top 200)
@app.route('/current_week_leaderboard', methods=['GET'])
def current_week_leaderboard():
    leaderboard = get_current_week_leaderboard()
    return render_template("currentweek.html",leaderboard=leaderboard)

# API 2: Display last week leaderboard given a country by the user (Top 200)
@app.route('/last_week_leaderboard/<string:country_code>', methods=['GET'])
def last_week_leaderboard(country_code):
    print(country_code)
    leaderboard = get_last_week_leaderboard_by_country(country_code)
    return render_template("lastweek.html",leaderboard=leaderboard)
    

# API 3: Fetch user rank, given the userId
@app.route('/user_rank/<string:user_id>', methods=['GET'])
def user_rank(user_id):
    rank = get_user_rank(user_id)
    if rank is not None:
        return jsonify({'user_id': user_id, 'rank': rank})
    else:
        return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
