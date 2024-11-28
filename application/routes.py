from application import app, mongo, bcrypt,db
from flask import render_template, request, redirect, flash, url_for
from .forms import LivresForm,RegistrationForm, LoginForm,ReservationForm
from bson.objectid import ObjectId
from flask_login import login_user, current_user, logout_user ,login_required
from .models import User
from .decorators import role_required
from datetime import datetime,timedelta



@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = mongo.db.utilisateurs.find_one({"email": form.email.data})
        if existing_user:
            flash('Cet email est déjà utilisé. Veuillez en choisir un autre.', 'danger')
            return redirect(url_for('inscription'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')        
        user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "role": form.role.data
        }
        mongo.db.utilisateurs.insert_one(user)
        flash('Votre compte a été créé avec succès !', 'success')
        return redirect(url_for('login')) 
    return render_template('inscription.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_data = mongo.db.utilisateurs.find_one({"email": form.email.data})
        if user_data and bcrypt.check_password_hash(user_data['password'], form.password.data):
            user_obj = User(user_data['_id'], user_data['email'], user_data['password'], user_data['role'])
            login_user(user_obj)
            flash('Connexion réussie', 'success')
            return redirect(url_for('dashboard_user')) 
        else:
            flash('Échec de la connexion. Vérifiez vos identifiants', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard_user')
def dashboard_user():
    return render_template('dashboard_user.html')



@app.route('/logout')
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))



@app.route('/')
def index():
    return render_template('index.html')


#ADMIN:
@app.route('/liste_livres')
def liste_livres():
    livres = db.livres.find() 
    return render_template('liste_livres.html', livres=livres)

@app.route('/modifier_livre/<id>', methods=['GET', 'POST'])
def modifier_livre(id):
    livre = db.livres.find_one({"_id": ObjectId(id)})
    form = LivresForm(data=livre)

    if request.method == 'POST' and form.validate_on_submit():
        db.livres.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                'titre': form.titre.data,
                'auteur': form.auteur.data,
                'genre': form.genre.data,
                'annee_publication': form.annee_publication.data,
                'ISBN': form.ISBN.data,
                'statut': form.statut.data
            }}
        )
        flash('Livre modifié avec succès !', 'success')
        return redirect(url_for('liste_livres'))

    return render_template('modifier_livre.html', form=form, livre=livre)

@app.route('/confirmer_suppression_livre/<id>')
def confirmer_suppression_livre(id):
    livre = db.livres.find_one({"_id": ObjectId(id)})
    return render_template('supprimer.html', livre=livre)
@app.route('/supprimer_livre/<id>', methods=['POST'])
def supprimer_livre(id):
    db.livres.delete_one({"_id": ObjectId(id)})  
    flash('Livre supprimé avec succès !', 'success')  
    return redirect(url_for('liste_livres')) 


@app.route('/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre():
    if request.method == "POST":
        form = LivresForm(request.form)
        livre_titre=form.titre.data
        livre_auteur= form.auteur.data
        livre_genre= form.genre.data
        livre_annee_publication= form.annee_publication.data
        livre_ISBN= form.ISBN.data
        livre_statut= form.statut.data
        
        db.livres.insert_one({
             "titre": form.titre.data,
            "auteur": form.auteur.data,
            "genre": form.genre.data,
            "annee_publication": form.annee_publication.data,
            "ISBN": form.ISBN.data,
            "statut": form.statut.data
        })
        flash("Livre ajouté avec succès !", "success")
        return redirect(url_for('liste_livres'))
    else:
        form = LivresForm()
    return render_template("ajouter_livre.html", form = form)


#USER : 
@app.route('/bibliotheque')
def bibliotheque():
    livres = mongo.db.livres.find()
    return render_template('bibliotheque.html', livres=livres)

from datetime import datetime
from bson import ObjectId
from flask import request, redirect, url_for, flash

@app.route('/reserver_livre/<livre_id>', methods=['POST'])
def reserver_livre(livre_id):
    if not current_user.is_authenticated:
        flash("Vous devez être connecté pour réserver un livre.", "danger")
        return redirect(url_for('login'))

    livre = mongo.db.livres.find_one({"_id": ObjectId(livre_id)})
    
    if not livre or livre.get("statut") != "disponible":
        flash("Livre non disponible pour réservation.", "danger")
        return redirect(url_for('liste_livre'))
    date_debut_str = request.form.get("date_debut")
    date_fin_str = request.form.get("date_fin")
    try:
        date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d')
        date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d')
    except ValueError:
        flash("Les dates sont invalides.", "danger")
        return redirect(url_for('liste_livre'))
    if date_fin <= date_debut:
        flash("La date de fin doit être après la date de début.", "danger")
        return redirect(url_for('liste_livre'))
    reservation = {
        "utilisateur_id": ObjectId(current_user.id),
        "livre_id": ObjectId(livre_id),
        "date_debut": date_debut,
        "date_fin": date_fin,
        "statut": "active"
    }
    mongo.db.reservations.insert_one(reservation)
    mongo.db.livres.update_one(
        {"_id": ObjectId(livre_id)},
        {"$set": {"statut": "réservé"}}
    )

    flash("Le livre a été réservé avec succès.", "success")
    return redirect(url_for('mes_reservations'))



@app.route('/mes_reservations')
def mes_reservations():
    reservations = mongo.db.reservations.find({"utilisateur_id": ObjectId(current_user.id), "statut": "active"})
    livres_reserves = [
        {
            "livre": mongo.db.livres.find_one({"_id": reservation["livre_id"]}),
            "reservation": reservation
        }
        for reservation in reservations
    ]
    return render_template("mes_reservations.html", livres_reserves=livres_reserves)


@app.route('/emprunter_livre/<livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    livre = mongo.db.livres.find_one({"_id": ObjectId(livre_id), "statut": "disponible"})
    if livre:
        emprunt = {
            "livre_id": ObjectId(livre_id),
            "utilisateur_id": ObjectId(current_user.id),
            "date_debut": datetime.now().strftime('%Y-%m-%d'),
            "date_retour": (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            "statut": "emprunté"
        }
        mongo.db.emprunts.insert_one(emprunt)
        mongo.db.livres.update_one({"_id": ObjectId(livre_id)}, {"$set": {"statut": "emprunté"}})
        flash('Le livre a été emprunté avec succès.', 'success')
    else:
        flash('Ce livre est déjà emprunté ou réservé.', 'danger')

    return redirect(url_for('bibliotheque'))

@app.route('/mes_emprunts')
@login_required 
def mes_emprunts():
    emprunts = mongo.db.emprunts.find({"utilisateur_id": ObjectId(current_user.id), "statut": "emprunté"})
    livres_empruntes = []
    for emprunt in emprunts:
        livre = mongo.db.livres.find_one({"_id": emprunt['livre_id']})
        if livre:
            livre['emprunt'] = emprunt
            livres_empruntes.append(livre)

    return render_template('mes_emprunts.html', livres=livres_empruntes)
