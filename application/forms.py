from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField , PasswordField,DateField
from wtforms.validators import DataRequired, Length, NumberRange,Email, EqualTo


class LivresForm(FlaskForm):
    titre = StringField('Titre', validators=[DataRequired(), Length(min=2, max=100)])
    auteur = StringField('Auteur', validators=[DataRequired(), Length(min=2, max=100)])
    genre = StringField('Genre', validators=[DataRequired(), Length(min=2, max=50)])
    annee_publication = IntegerField('Année de publication', validators=[DataRequired(), NumberRange(min=1000, max=9999)])
    ISBN = StringField('ISBN', validators=[DataRequired(), Length(min=10, max=13)])
    statut = SelectField('Statut', choices=[('disponible', 'Disponible'), ('reserve', 'Réservé'), ('emprunte', 'Emprunté')], validators=[DataRequired()])
    submit = SubmitField('Ajouter le livre')


class RegistrationForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rôle', choices=[('etudiant', 'Étudiant'), ('enseignant', 'Enseignant'), ('admin', 'Administrateur')], validators=[DataRequired()])
    submit = SubmitField('S’inscrire')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class ReservationForm(FlaskForm):
    date_debut = DateField('Date de début', format='%Y-%m-%d', validators=[DataRequired()])
    date_fin = DateField('Date de fin', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Réserver')
