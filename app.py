from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql+psycopg2://postgres:[password]c@localhost:5432/mtasubwaydelays'
# Debugging line to print the URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'secret_key'
db=SQLAlchemy(app)




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
    return render_template('index.html')




@app.route("/subscribe", methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        existing_email =EmailData.query.filter_by(email=email).first()
        if existing_email:
            flash("You are already subscribing!")
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

