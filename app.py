from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow

from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from flask_mail import Mail, Message


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'investors_details.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'super-secret'  # change this IRL

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '0173e9d27d56cc'
app.config['MAIL_PASSWORD'] = '7824347a5b7ba1'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)

jwt = JWTManager(app)

mail = Mail(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


@app.cli.command('db_seed')
def db_seed():
    t_inv1 = iDetails(inv_name='human',
                      inv_type='tech',
                      equity=12365.12,
                      no_of_members=3,
                      cash_at_hand=234.23,
                      interested_investing='something',
                      role='founder',
                      imgfile='image',
                      invested_companies='tech',
                      list_of_companies='tech1',
                      # kyc upload files
                      Adhar_card_front='adharfront',
                      Adhar_card_back='adharback',
                      pan='pan card',
                      bank_Statement='bank statement'
)

    db.session.add(t_inv1)

    test_user = Investor(fname = 'manoj',
                        lname='bajpai',
                     phone = 23984738,
                     email = 'email@email.com',
                     password = 'ashishj')

    db.session.add(test_user)
    db.session.commit()
    print('Database seeded!')



@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from the Investry API.'), 200


@app.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found'), 404


@app.route('/age_verify/<string:name>/<int:age>')
def url_variables(name: str, age: int):
    if age < 18:
        return jsonify(message="Sorry " + name + ", you are not old enough."), 401
    else:
        return jsonify(message="Welcome " + name + ", you are old enough!")


@app.route('/investors_details', methods=['GET'])
def investors_details():
    inv_list = iDetails.query.all()
    result = invs_schema.dump(inv_list)
    return jsonify(result.data)


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test1 = Investor.query.filter_by(email=email).first()
    phone = request.form['phone']
    test2 = Investor.query.filter_by(phone=phone).first()
    if test1:
        return jsonify(message='That email already exists.'), 409
    if test2:
        return jsonify(message='That phone already exists.'), 409
    if test1 and test2:
        return jsonify(message='phone and email already exists.'), 409
    
    else:
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']
        investor = Investor(fname=fname,lname=lname,phone=phone, email=email,
                        password=password)
        db.session.add(investor)
        db.session.commit()
        return jsonify(message="Investor created successfully."), 201



@app.route('/login_investor', methods=['POST'])
def login_investor():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = Investor.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!", access_token=access_token)
    else:
        return jsonify(message="Bad email or password"), 401



@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    investor = Investor.query.filter_by(email=email).first()
    if investor:
        msg = Message("your investry API password is " + investor.password,
                      sender="admin@investry-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to " + email)
    else:
        return jsonify(message="That email doesn't exist"), 401

#read

@app.route('/Inv_details/<int:inv_id>', methods=["GET"])
def inv_details(inv_id: int):
    investor_dtl = iDetails.query.filter_by(inv_id=inv_id).first()
    if investor_dtl:
        result = inv_schema.dump(investor_dtl)
        return jsonify(result.data)
    else:
        return jsonify(message="That investor_dtl does not exist"), 404


#create

'''
@app.route('/add_investor_details', methods=['POST'])
@jwt_required
def add_investor_details():
    inv_name = request.form['inv_name']
    test = iDetails.query.filter_by(inv_name=inv_name).first()
    if test:
        return jsonify("There is already a investor_dtl by that name"), 409
    else:
        inv_type = request.form['inv_type']
        inv_name = request.form['inv_name']
        role = request.form['role']
        equity = float(request.form['equity'])
        no_of_members = int(request.form['no_of_members'])
        cash_at_hand=float(request.form['cash_at_hand'])
        interested_investing = request.form['interested_investing']
         #upload
        imgfile = request.form['imgfile']
        invested_companies = request.form['invested_companies']
        list_of_companies = request.form['list_of_companies']
        # kyc upload files
        Adhar_card_front = request.form['Adhar_card_front']
        Adhar_card_back = request.form['Adhar_card_back']
        pan = request.form['pan']
        bank_statement = request.form['bank_Statement']

        new_inv = iDetails(inv_name=inv_name,
                           inv_type=inv_type,
                           role=role,
                           equity=equity,
                           # no_of_members=no_of_members,
                           # cash_at_hand=cash_at_hand,
                           interested_investing='tech and healthcare',
                           imgfile=imgfile,
                           # table of companies investes
                           # invested_companies = invested_companies,
                           # list_of_companies = list_of_companies,
                           # kyc upload files
                           Adhar_card_front=Adhar_card_front,
                           Adhar_card_back=Adhar_card_back,
                           pan=pan,
                           bank_statement=bank_statement

                           )

        db.session.add(new_inv)
        db.session.commit()
        return jsonify(message="You added a investor details"), 201
'''

#update

'''
@app.route('/update_investors', methods=['PUT'])
@jwt_required
def update_investors():
    inv_id = int(request.form['inv_id'])
    investor_dtl = iDetails.query.filter_by(inv_id=inv_id).first()
    if investor_dtl:
        investor_dtl.inv_name = request.form['inv_name']
        investor_dtl.inv_type = request.form['inv_type']
        investor_dtl.role = request.form['role']
        investor_dtl.equity = float(request.form['equity'])
        investor_dtl.inv_id = int(request.form['no_of_members '])
        investor_dtl.cash_at_hand = float['cash_at_hand = Column(Float)']
        investor_dtl.interested_investing = request.form['interested_investing']
        investor_dtl.role = request.form['role']
        # upload
        investor_dtl.imgfile = request.form['imgfile']
        investor_dtl.invested_companies = request.form['invested_companies']
        investor_dtl.list_of_companies = request.form['list_of_companies']
        # kyc upload files
        investor_dtl.Adhar_card_front = request.form['Adhar_card_front']
        investor_dtl.Adhar_card_back = request.form['Adhar_card_back']
        investor_dtl.pan = request.form['pan']
        investor_dtl.bank_Statement = request.form['bank_Statement']

        db.session.commit()
        return jsonify(message="You updated a investor_dtl"), 202
    else:
        return jsonify(message="That investor_dtl does not exist"), 404
'''

#delete
'''
@app.route('/remove_investors_details/<int:inv_id>', methods=['DELETE'])
@jwt_required
def remove_idetails(inv_id: int):
    investor_dtl = iDetails.query.filter_by(inv_id=inv_id).first()
    if investor_dtl:
        db.session.delete(investor_dtl)
        db.session.commit()
        return jsonify(message="You deleted a investor_dtl"), 202
    else:
        return jsonify(message="That investor_dtl does not exist"), 404

'''

# database models
class Investor(db.Model):
    __tablename__ = 'investor_u'
    id = Column(Integer, primary_key=True)
    fname = Column(String)
    lname = Column(String)
    phone = Column(Float, unique=True)
    email = Column(String, unique=True)
    password = Column(String)


class iDetails(db.Model):
    __tablename__ = 'investor_details'
    inv_id = Column(Integer, primary_key=True)
    inv_name = Column(String)
    inv_type = Column(String)
    equity = Column(Float)
    no_of_members = Column(Integer)
    cash_at_hand = Column(Float)
    interested_investing = Column(String)
    role = Column(String)
    imgfile = Column(String)
    invested_companies = Column(String)
    list_of_companies = Column(String)
    # kyc upload files
    Adhar_card_front = Column(String)
    Adhar_card_back = Column(String)
    pan = Column(String)
    bank_Statement = Column(String)

class InvestorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'fname','lname', 'phone', 'email', 'password')


class InvSchema(ma.Schema):
    class Meta:
        fields = ('inv_id', 'inv_name', 'inv_type', 'equity', 'no_of_members', 'cash_at_hand', 'interested_investing',
                   'role', 'imgfile', 'invested_companies', 'list_of_companies', 'Adhar_card_front',
                  'Adhar_card_back',
                  'pan', 'bank_Statement'
                  )

investor_schema = InvestorSchema()
investors_schema = InvestorSchema(many=True)

inv_schema = InvSchema()
invs_schema = InvSchema(many=True)


if __name__ == '__main__':
app.run(host='0.0.0.0',port=3000)
