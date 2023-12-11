import datetime

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# Initialize the CKEditor
ckeditor = CKEditor(app)
Bootstrap5(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class CreatePostForm(FlaskForm):
    title = StringField('Blog PostTitle', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    author = StringField('Your Name', validators=[DataRequired()])
    url = StringField('Blog Image URL', validators=[DataRequired(), URL()])
    body = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit Post')


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # Query the database for all the posts. Convert the data to a python list.
    posts = []
    with app.app_context():
        results = db.session.execute(db.select(BlogPost).order_by(BlogPost.date))
        posts = results.scalars().all()
    return render_template("index.html", all_posts=posts)


# Add a route so that you can click on individual posts.
@app.route('/post/<post_id>')
def show_post(post_id):
    # Retrieve a BlogPost from the database based on the post_id
    with app.app_context():
        requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    return render_template("post.html", post=requested_post)


# add_new_post() to create a new blog post
@app.route('/new-post', methods=['GET', 'POST'])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        today = datetime.datetime.now()
        with app.app_context():
            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                date=today.strftime("%B %d, %Y"),
                body=form.body.data,
                author=form.author.data,
                img_url=form.url.data,
            )
            db.session.add(new_post)
            db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form, new_post=True)


# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    with app.app_context():
        post_to_edit = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    form = CreatePostForm(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        img_url=post_to_edit.img_url,
        author=post_to_edit.author,
        body=post_to_edit.body
    )

    if form.validate_on_submit():
        with app.app_context():
            post_to_update = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
            post_to_update.title = form.title.data
            post_to_update.subtitle = form.subtitle.data
            post_to_update.img_url = form.url.data
            post_to_update.author = form.author.data
            post_to_update.body = form.body.data
            db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))

    return render_template('make-post.html', form=form, new_post=False)


# TODO: delete_post() to remove a blog post from the database
@app.route('/delete/<post_id>')
def delete_post(post_id):
    with app.app_context():
        post_to_delete = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
        db.session.delete(post_to_delete)
        db.session.commit()
    return redirect(url_for('get_all_posts'))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
