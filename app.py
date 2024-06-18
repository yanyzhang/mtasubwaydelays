from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql+psycopg2://postgres:groe46disc@localhost:5432/mtasubwaydelays'
# Debugging line to print the URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)




class EmailData(db.Model):
    __tablename__ = "email_list"
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.SmallInteger, nullable=False)

    def __init__(self, email):
        self.email=email


with app.app_context():
    db.create_all()



@app.route("/")
def index():
    return render_template('index.html')




@app.route("/subscript", methods=['POST'])
def subscript():
    if request.method=='POST':
        email=request.form['email_name']
        print(request.form)

        subscriptionlist=EmailData(email)
        db.session.add(subscriptionlist)
        db.session.commit()

        flash("Thank you for subscribing to MTA Subway Delays!")
        return render_template('index.html')




if __name__=='__main__':
    app.debug=True
    app.run()

