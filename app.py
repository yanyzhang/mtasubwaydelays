from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql+psycopg2://postgres:groe46disc@localhost:5432/mtasubwaydelays'
# Debugging line to print the URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)



with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template('index.html')

# @app.route("/thankyou", method=['POST'])
# def thankyou():
#     if request.method=='POST':
#         email=request.form['email_name']

#         return render_template('thankyou.html')









if __name__=='__main__':
    app.debug=True
    app.run()

