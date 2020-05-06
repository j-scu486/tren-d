from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, HiddenField, SelectField, SelectMultipleField, widgets, RadioField
from wtforms.validators import DataRequired, Email, Length

# Need to add VALIDATION

class AddToCart(FlaskForm):
    quantity = SelectField('Quantity', choices=[(i, i) for i in range(1,20)], coerce=int)
    size = SelectField('Size', choices=[("",""),('L', 'L'), ('M', 'M'), ('S', 'S')], validators=[DataRequired()], coerce=str)
    id = HiddenField()
    submit_add = SubmitField('Add to Cart')
    submit_update = SubmitField('Update Quantity')

class OrderForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name =  StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    postal_code = IntegerField('Post Code', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Proceed to Checkout')

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SearchForm(FlaskForm):
    price = RadioField('Price', choices=[('100', '0 - $100'), ('200', '$200 - $300'), ('300', '$300 - $400')])
    color = MultiCheckboxField('Color', choices=[('red', 'Red'), ('black', 'Black'), ('blue', 'Blue')])
    size = MultiCheckboxField('Size', choices=[('L', 'L'), ('M', 'M'), ('S', 'S')])
