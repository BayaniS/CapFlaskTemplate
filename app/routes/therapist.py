# These routes are an example of how to use data, forms and routes to create
# a forum where a posts and comments on those posts can be
# Created, Read, Updated or Deleted (CRUD)

from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Comment, Therapist
from app.classes.forms import TherapistForm
from flask_login import login_required
import datetime as dt


@app.route('/therapist/list')
def therapistList():
    # This retrieves all of the 'posts' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'posts'.
    therapists = Therapist.objects()
    # This renders (shows to the user) the posts.html template. it also sends the posts object 
    # to the template as a variable named posts.  The template uses a for loop to display
    # each post.
    return render_template('therapists.html',therapists=therapists)

# This route will get one specific post and any comments associated with that post.  
# The postID is a variable that must be passsed as a parameter to the function and 
# can then be used in the query to retrieve that post from the database. This route 
# is called when the user clicks a link on postlist.html template.
# The angle brackets (<>) indicate a variable. 
@app.route('/therapist/<therapistID>')
# This route will only run if the user is logged in.

def therapist(therapistID):
    # retrieve the post using the postID
    thisTherapist = Therapist.objects.get(id=therapistID)

    return render_template('therapist.html',therapist=thisTherapist)

# This route will delete a specific post.  You can only delete the post if you are the author.
# <postID> is a variable sent to this route by the user who clicked on the trash can in the 
# template 'post.html'. 
# TODO add the ability for an administrator to delete posts. 
@app.route('/therapist/delete/<therapistID>')
# Only run this route if the user is logged in.
@login_required
def therapistDelete(therapistID):
    # retrieve the post to be deleted using the postID
    deleteTherapist = Therapist.objects.get(id=therapistID)
    # check to see if the user that is making this request is the author of the post.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteTherapist.author:
        # delete the post using the delete() method from Mongoengine
        deleteTherapist.delete()
        # send a message to the user that the post was deleted.
        flash('The Entry was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a entry you don't own.")
    # Retrieve all of the remaining posts so that they can be listed.
    therapists = Therapist.objects()  
    # Send the user to the list of remaining posts.
    return render_template('therapists.html',therapists=therapists)

# This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new post based on what the user put in the form.
# Because this route includes a form that both gets and posts data it needs the 'methods'
# in the route decorator.
@app.route('/therapist/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def therapistNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = TherapistForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new post form. 
        # Post() is a mongoengine method for creating a new post. 'newPost' is the variable 
        # that stores the object that is the result of the Post() method.  
        newTherapist = Therapist(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            title = form.title.data,
            desc = form.desc.data,
            agerange = form.agerange.data,
            location = form.location.data,
            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modifydate = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newTherapist.save()

        # Once the new post is saved, this sends the user to that post using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a post so we want 
        # to send them to that post. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('therapist', therapistID=newTherapist.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at postform.html to 
    # see how that works.
    return render_template('therapistform.html',form=form)


# This route enables a user to edit a post.  This functions very similar to creating a new 
# post except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original post. Read and understand the new post route 
# before this one. 
@app.route('/therapist/edit/<therapistID>', methods=['GET', 'POST'])
@login_required
def therapistEdit(therapistID):
    editTherapist = Therapist.objects.get(id=therapistID)
    # if the user that requested to edit this post is not the author then deny them and
    # send them back to the post. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editTherapist.author:
        flash("You can't edit a entry you don't own.")
        return redirect(url_for('therapist',therapistID=therapistID))
    # get the form object
    form = TherapistForm()
    # If the user has submitted the form then update the post.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editTherapist.update(
            title = form.title.data,
            desc = form.desc.data,
            agerange = form.agerange.data,
            location = form.location.data,
            modifydate = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated post using a redirect.
        return redirect(url_for('therapist',therapistID=therapistID))

    # if the form has NOT been submitted then take the data from the editPost object
    # and place it in the form object so it will be displayed to the user on the template.
    form.title.data = editTherapist.title
    form.desc.data = editTherapist.desc
    form.agerange.data = editTherapist.agerange
    form.location.data = editTherapist.location

    # Send the user to the post form that is now filled out with the current information
    # from the form.
    return render_template('therapistform.html',form=form)

#####

