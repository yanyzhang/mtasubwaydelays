from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func,extract
from collections import defaultdict
from datetime import datetime



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql+psycopg2://postgres:groe46disc@localhost:5432/mtasubwaydelays'
# Debugging line to print the URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'secret_key'
db=SQLAlchemy(app)

class SubwayDelays(db.Model):
    __tablename__="subway_delays"
    id=db.Column(db.Integer, primary_key=True)
    subwayline=db.Column(db.String(1))
    stationname=db.Column(db.String(255))
    date=db.Column(db.Date)
    delayminutes=db.Column(db.SmallInteger, nullable=False)

    def __init__(self, subwayline, stationname, date, delayminutes):
        self.subwayline = subwayline.upper()
        self.stationname = stationname.upper()
        self.date = date
        self.delayminutes = delayminutes

    def __repr__(self):
        return f'<SubwayDelays {self.subwayline} {self.stationname} {self.date} {self.delayminutes}>'


class EmailData(db.Model):
    __tablename__ = "email_list"
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, email):
        self.email=email


with app.app_context():
    db.create_all()



@app.route("/")
def index():
    statistics = {}
    lines = db.session.query(SubwayDelays.subwayline,  func.avg(SubwayDelays.delayminutes).label('avg_delay')).group_by(SubwayDelays.subwayline).all()

    for line,  avg_delay in lines:
        statistics[line] = {
            # 'total_delays': total_delays,
            'avg_delay': round(avg_delay)
        }
    top_lines = db.session.query(SubwayDelays.subwayline, func.count(SubwayDelays.id).label('total_delays')).group_by(SubwayDelays.subwayline).order_by(func.count(SubwayDelays.id).desc()).limit(3).all()

    date_summary = defaultdict(lambda: {'total_delays': 0, 'avg_delay': 0.0})
    date_delays = db.session.query(extract('day', SubwayDelays.date).label('day'), extract('month', SubwayDelays.date).label('month'), extract('year', SubwayDelays.date).label('year'), func.count(SubwayDelays.id).label('total_delays'), func.avg(SubwayDelays.delayminutes).label('avg_delay')).group_by(extract('day', SubwayDelays.date), extract('month', SubwayDelays.date), extract('year', SubwayDelays.date)).all()

    for day, month, year, total_delays, avg_delay in date_delays:
        date_str = f"{year}-{month}-{day}"
        date_summary[date_str]['total_delays'] = total_delays
        date_summary[date_str]['avg_delay'] = round(avg_delay)

    latest_delays = SubwayDelays.query.order_by(SubwayDelays.date.desc()).limit(10).all()
    table_headers = ['Date', 'Subway Line', 'Station Name', 'Delay Minutes']

    top_delayed_lines = db.session.query(SubwayDelays.subwayline, db.func.sum(SubwayDelays.delayminutes).label('total_delay')) \
                                  .group_by(SubwayDelays.subwayline) \
                                  .order_by(db.desc('total_delay')) \
                                  .limit(5) \
                                  .all()
    ranked_lines = [(index + 1, line.subwayline) for index, line in enumerate(top_delayed_lines)]

    return render_template('index.html', statistics=statistics, top_lines=top_lines,date_summary=date_summary, latest_delays=latest_delays, table_headers=table_headers, top_delayed_lines=top_delayed_lines, ranked_line=ranked_lines)
  

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

# @app.route("/newdelays")
# def newdelays():
#     return render_template('newdelays.html')

@app.route('/newdelays',methods=['GET','POST'])
def newdelays():
    today_date = datetime.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        subwayline=request.form['subwayline']
        stationname=request.form['stationname']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        # date=request.form['date']
        delayminutes=request.form['delayminutes']

        new_subwaydelays=SubwayDelays(subwayline=subwayline, stationname=stationname, date=date, delayminutes=delayminutes)
        db.session.add(new_subwaydelays)
        db.session.commit()
        flash('Delay reported successfully!', 'success')

        return render_template('newdelays.html', today_date=today_date, show_flash=True)
    return render_template('newdelays.html', today_date=today_date, show_flash=False)



@app.route("/subscribe", methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        existing_email =EmailData.query.filter_by(email=email).first()
        if existing_email:
            flash("You are already subscribing!", 'success')
            return redirect(url_for('index'))


        # email=request.form["email_name"]
        # print(request.form)

        subscriptionlist=EmailData(email)
        db.session.add(subscriptionlist)
        db.session.commit()

        # flash("Thank you for subscribing to MTA Subway Delays!")
        return render_template("subscribe.html")
    else:
        flash("Bad Request", "danger")
        return redirect(url_for('index'))



if __name__=='__main__':
    app.debug=True
    app.run()

