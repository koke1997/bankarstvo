from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField
from wtforms.validators import InputRequired

class TransferForm(FlaskForm):
    recipient = StringField('Recipient Username', validators=[InputRequired()])
    account_choice = SelectField('Select Account', coerce=int, validators=[InputRequired()])
    transfer_amount = DecimalField('Transfer Amount', validators=[InputRequired()])
