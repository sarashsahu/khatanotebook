from flask import Flask, render_template, request, jsonify, session, redirect, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import pandas as pd
import io
import datetime
from utils import generate_otp, generate_html_email_body

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Mail Config
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='ENTER YOUR GMAIL ID',
    MAIL_PASSWORD='ENTER YOUR GMAIL APP PASSWORD',
    MAIL_DEFAULT_SENDER=('Team - Khata Notebook', 'infam0usxdxdx@gmail.com')
)
mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    otp = db.Column(db.String(10))
    otp_generated_at = db.Column(db.DateTime)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    person = db.Column(db.String(50))
    desc = db.Column(db.String(100))
    amount = db.Column(db.Float)
    date = db.Column(db.String(20))

# ----------------- Routes --------------------

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Try login.')
            return redirect('/')
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        flash('Registered! Please log in.')
        return redirect('/')
    return render_template('register.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.form['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Email not registered. Please register first.')
        return redirect('/register')

    otp = generate_otp()
    user.otp = otp
    user.otp_generated_at = datetime.datetime.now()
    db.session.commit()

    html = generate_html_email_body(user.name, otp)
    msg = Message('Your OTP - Khata Notebook', recipients=[email])
    msg.html = html
    mail.send(msg)

    session['email'] = email
    return render_template('verify_otp.html')

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    otp_input = request.form['otp']
    email = session.get('email')
    user = User.query.filter_by(email=email).first()

    if user and user.otp == otp_input:
        if (datetime.datetime.now() - user.otp_generated_at).total_seconds() > 300:
            flash('OTP expired. Please request again.')
            return redirect('/')
        session['user'] = user.email
        return redirect('/dashboard')

    flash('Invalid OTP.')
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', email=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ----------------- API --------------------

@app.route('/api/entries')
def get_entries():
    if 'user' not in session:
        return jsonify({})
    user_email = session['user']
    entries = Entry.query.filter_by(user_email=user_email).all()
    result = {}
    for e in entries:
        result.setdefault(e.person, []).append({
            "desc": e.desc,
            "amount": e.amount,
            "date": e.date
        })
    return jsonify(result)

@app.route('/api/entry', methods=['POST'])
def add_entry():
    if 'user' not in session:
        return 'Unauthorized', 401

    data = request.get_json()
    entry = Entry(
        user_email=session['user'],
        person=data['person'],
        desc=data['desc'],
        amount=data['amount'],
        date=data['date']
    )
    db.session.add(entry)
    db.session.commit()
    return '', 204

@app.route('/api/entry', methods=['DELETE'])
def delete_entry():
    if 'user' not in session:
        return 'Unauthorized', 401

    data = request.get_json()
    person = data['person']
    index = data.get('index')
    user_email = session['user']
    query = Entry.query.filter_by(user_email=user_email, person=person)

    if index is not None:
        entries = query.all()
        if 0 <= index < len(entries):
            db.session.delete(entries[index])
    else:
        query.delete()
    db.session.commit()
    return '', 204

@app.route('/api/edit-entry', methods=['PUT'])
def edit_entry():
    if 'user' not in session:
        return 'Unauthorized', 401

    data = request.get_json()
    person = data['person']
    index = data['index']
    new_desc = data['desc']
    new_amount = data['amount']
    user_email = session['user']

    entries = Entry.query.filter_by(user_email=user_email, person=person).all()
    if 0 <= index < len(entries):
        entry = entries[index]
        entry.desc = new_desc
        entry.amount = new_amount
        db.session.commit()
        return '', 204
    return 'Entry not found', 404

@app.route('/api/person', methods=['DELETE'])
def delete_person():
    if 'user' not in session:
        return 'Unauthorized', 401

    data = request.get_json()
    person = data['person']
    user_email = session['user']

    Entry.query.filter_by(user_email=user_email, person=person).delete()
    db.session.commit()
    return '', 204

@app.route('/export-excel', methods=['POST'])
def export_excel():
    if 'user' not in session:
        return 'Unauthorized', 401

    user_email = session['user']
    entries = Entry.query.filter_by(user_email=user_email).all()

    if not entries:
        return 'No data', 400

    df = pd.DataFrame([{
        'Name': e.person,
        'Reason': e.desc,
        'Amount': e.amount,
        'Date': e.date
    } for e in entries])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Khata')
    buffer.seek(0)

    # Send email backup
    user = User.query.filter_by(email=user_email).first()

    if user:
        # Prepare email with Excel attachment
        msg = Message(
            subject="📒 Your Khata Notebook - Excel Backup",
            recipients=[user.email]
        )
        
        msg.body = (
            f"Hello {user.name},\n\n"
            f"Attached is your Khata Notebook backup in Excel format.\n"
            f"Feel free to keep it for your records.\n\n"
            f"Best regards,\n"
            f"Team Khata Notebook"
        )
        
        msg.attach(
            filename="Khata_Notebook.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            data=buffer.read()
        )
        
        mail.send(msg)

    # Reset buffer position before sending as HTTP response
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Khata_Notebook.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ----------------- Run --------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
