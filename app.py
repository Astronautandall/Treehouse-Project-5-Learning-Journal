from datetime import datetime
from urllib.parse import quote, unquote

from flask import (Flask, g, render_template, flash, url_for, redirect, abort,
                   request)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from slugify import slugify

import forms
import models



DEBUG = True
PORT = 5000
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = "All them lil dudes can't stand beside me"

# Login manager options
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""

    g.db = models.DATABASE
    g.db.get_conn()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/')
@login_required
def index():
    entries = models.Entry.select().limit(100)
    for entry in entries:
        tags = models.EntryTag.get_entry_tags(entry.id)

        # Creating the links for the list of entries with the tag
        tags_html = ""
        for tag in tags:
            #Encoding the url for more safe search
            url_encoded_tag = quote(tag.tag.encode('utf-8'))
            tags_html += "<a href='/entries/tag/{}'>{}</a> ".format(url_encoded_tag, tag.tag)

        entry.tags = tags_html
    
    return render_template('index.html', entries=entries)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()

    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match", "error")

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out!", "success")
    return redirect(url_for('index'))


@app.route('/entry/add', methods=('GET', 'POST'))
@login_required
def entry_add():
    """Add an entry"""
    form = forms.EntryForm()
    if form.validate_on_submit():

        entry_data = {
            'title': form.title.data,
            'date': form.date.data,
            'time_spent': form.time_spent.data,
            'what_i_learned': form.what_i_learned.data,
            'sources_to_remember': form.sources_to_remember.data,
            'tags' : form.tags.data
        }

        models.Entry.create_entry(**entry_data)

        flash("Nice, the entry has been added", "error")
        return redirect(url_for('index'))

    return render_template('new.html', form=form)

@app.route('/entries/entries/<slug>')
def details(slug):
    """Show the details of an entry"""
    try:
        entry = models.Entry.select().where(models.Entry.slug == slug).get()

        tags = models.EntryTag.get_entry_tags(entry.id)

        # Creating the links for the list of entries with the tag
        tags_html = ""
        for tag in tags:
            #Encoding the url for more safe search
            url_encoded_tag = quote(tag.tag.encode('utf-8'))
            tags_html += "<a href='/entries/tag/{}'>{}</a> ".format(url_encoded_tag, tag.tag)

        entry.tags = tags_html

    except models.DoesNotExist:
        abort(404)
    else:
        return render_template('detail.html', entry=entry)

@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
def edit(slug):
    """ Edits an entry"""
    try:
        entry = models.Entry.select().where(models.Entry.slug == slug).get()
    except model.DoesNotExist:
        abort(404)
    else:

        tags = models.EntryTag.get_entry_tags(entry.id)
        tags = "" if tags.count() == 0 else ", ".join([ tag.tag for tag in tags])

        data = {
            'date' : entry.date
        }

        entry.date = entry.date.strftime('%d-%m-%Y')
        entry.tags = tags
        form = forms.EntryForm(obj=entry)

        if form.validate_on_submit():

            entry.title = form.title.data
            entry.slug = slugify(form.title.data)
            entry.date = form.date.data
            entry.time_spent = form.time_spent.data
            entry.sources_to_remember = form.sources_to_remember.data
            entry.save()

            for tag in form.tags.data.split(','):
                tag, created = models.Tag.get_or_create(tag=tag.strip())
                models.EntryTag.get_or_create(id_entry=entry.id, id_tag=tag.id)

            flash('Nice','success')
            return redirect(url_for('details', slug=entry.slug))

        return render_template('edit.html', form=form)

@app.route('/entries/delete/<slug>')
def delete(slug):
    """Deletes an entry"""

    try:
        entry = models.Entry.get(models.Entry.slug==slug)
    except models.DoesNotExist:
        abort(404)
    else:
        entry.delete_instance()
        flash('Nice, entry deleted', 'success')
        return redirect(url_for('index'))

@app.route('/entries/tag/<tag>')
def search_by_tag(tag):
    """Searchs entries by tag"""

    tag = unquote(tag)

    entries = (
        models.Entry
        .select()
        .join(models.EntryTag)
        .join(models.Tag)
        .where(models.Tag.tag==tag)
    )

    return render_template('index.html', entries=entries)



if __name__ == '__main__':

    models.initialize()

    # Creating a user for the login
    # It will be only created if it doesn't exists
    try: 
        models.User.create_user(
            email= 'techdegreestudent@treehouse.com',
            password='lemon pie'
        )
    except ValueError:
        pass

    app.run(debug=DEBUG, host=HOST, port=PORT)


