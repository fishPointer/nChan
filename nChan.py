### nChan - Eein's Private Imageboard / ADHD Lab Notebook ###
### June 16th, 2021

#IMPORTS
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#EXTERNAL URLS
breadnetUI = "http://96.38.188.104:1880/ui"
breadnetBackend = "http://96.38.188.104:1880/"
eeininfo = "https://eein.info/"

#INITIALIZE DB AND FLASK
app = Flask(__name__)
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:q@localhost:3306/nChan"

#DATABASE SCHEMA
#SPRINT NOTES - BOARD #1 - SP
class spBoard(db.Model):
    postid = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(16), nullable=False, default="Anonymous")
    subject = db.Column(db.String(64), default="[No Subject]")
    message = db.Column(db.String(8192), nullable=False)
    linknumber = db.Column(db.String(16))
    parentthread = db.Column(db.Integer)
    recentreply = db.Column(db.Integer, default=postid)

    def __init__(self, username, subject, message, linknumber, parentthread):
        self.username = username
        self.subject = subject
        self.message = message
        self.linknumber = linknumber
        self.parentthread = parentthread

    def __repr__(self):
        return '<Name %r>' % self.postid 

#RESEARCH - BOARD #2 - RS
class rsBoard(db.Model):
    postid = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(16), nullable=False, default="Anonymous")
    subject = db.Column(db.String(64), default="[No Subject]")
    message = db.Column(db.String(8192), nullable=False)
    linknumber = db.Column(db.String(16))
    parentthread = db.Column(db.Integer)
    recentreply = db.Column(db.Integer, default=postid)

    def __init__(self, username, subject, message, linknumber, parentthread):
        self.username = username
        self.subject = subject
        self.message = message
        self.linknumber = linknumber
        self.parentthread = parentthread

    def __repr__(self):
        return '<Name %r>' % self.postid 

#LAB MISC. - BOARD #3 - LS
class lsBoard(db.Model):
    postid = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(16), nullable=False, default="Anonymous")
    subject = db.Column(db.String(64), default="[No Subject]")
    message = db.Column(db.String(8192), nullable=False)
    linknumber = db.Column(db.String(16))
    parentthread = db.Column(db.Integer)
    recentreply = db.Column(db.Integer, default=postid)

    def __init__(self, username, subject, message, linknumber, parentthread):
        self.username = username
        self.subject = subject
        self.message = message
        self.linknumber = linknumber
        self.parentthread = parentthread

    def __repr__(self):
        return '<Name %r>' % self.postid 

#PROJECT NOTES - BOARD #4 - PN
class pnBoard(db.Model):
    postid = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(16), nullable=False, default="Anonymous")
    subject = db.Column(db.String(64), default="[No Subject]")
    message = db.Column(db.String(8192), nullable=False)
    linknumber = db.Column(db.String(16))
    parentthread = db.Column(db.Integer)
    recentreply = db.Column(db.Integer, default=postid)

    def __init__(self, username, subject, message, linknumber, parentthread):
        self.username = username
        self.subject = subject
        self.message = message
        self.linknumber = linknumber
        self.parentthread = parentthread

    def __repr__(self):
        return '<Name %r>' % self.postid 

#INIT
db.create_all()

###

#FUNCTIONS
#Parse Message String for Postlinks
def linkchecker(post_message):
    linkcheck = post_message.find(">>")
    cursor = linkcheck+2
    i=0
    extracted_link = ""
    post_message += ' '
    if linkcheck != -1:
        while (post_message[cursor+i]).isnumeric() and cursor+i < len(post_message) and post_message[cursor+i] != ' ':
            extracted_link += post_message[cursor+i]
            i += 1
    return extracted_link


###

#PAGES

#HOME
@app.route('/')
def home():
    return render_template('base.html', eeininfo=eeininfo, breadnetUI=breadnetUI, breadnetBackend=breadnetBackend)

#SP BOARD
@app.route('/sp/', methods=["POST", "GET"])
def sprint():
    title = "SPRINT NOTES"
    desc = "KAIZEN"
    url = '/sp/'
    parentthread = 0

    #POST SEQUENCE - New Thread
    if request.method == "POST":
        post_username = request.form['username']
        post_subject = request.form['subject']
        post_message = request.form['message']
        if not post_username:
            post_username = 'Anonymous'
        if not post_subject:
            post_subject = '[No Subject]'

        #Parse Message String for Postlinks
        extracted_link = linkchecker(post_message)

        #Declare Database Object 
        newpost = spBoard(post_username, post_subject, post_message, extracted_link, parentthread)

        #Attempt committing to DB and reload as GET
        try:
            #Add the new post
            db.session.add(newpost)
            db.session.commit()
            #Set new thread's recent reply to its own post ID so it bumps
            newpost.recentreply = newpost.postid
            db.session.commit()
            return redirect(url)
        except: 
            return "Failed to Post to Database"

    else:
        #GET method
        #Filter for Threads by descending bump
        chanthreads = spBoard.query.filter(spBoard.parentthread==0).order_by(spBoard.recentreply.desc())

        #Pull each thread's recent reply into a list
        childposts = []
        for chanthread in chanthreads:
            tag = chanthread.recentreply
            childposts.append(spBoard.query.get(tag))
        
        #Pass Parent and Child post lists into render function
        return render_template('lynxboard.html', boardtitle=title, boarddesc=desc, url=url, chanthreads=chanthreads, childposts=childposts)

@app.route('/sp/<int:postid>', methods=["POST", "GET"])
def sprintthread(postid):
    title = "SPRINT NOTES"
    desc = "KAIZEN"
    boardurl = '/sp/'
    url = '/sp/' + str(postid)
    threadnumber = spBoard.query.get_or_404(postid)
    parentthread = postid

    #POST method - Reply to Thread <postid>
    if request.method == "POST":
        post_username = request.form['username']
        post_message = request.form['message']
        post_subject = 'Reply'
        if not post_username:
            post_username = 'Anonymous'

        #Parse Message String for Postlinks
        extracted_link = linkchecker(post_message)

        #Declare Database Object
        newpost = spBoard(post_username, post_subject, post_message, extracted_link, parentthread)

        #Attempt committing to DB and reload as GET
        try:
            db.session.add(newpost)
            db.session.commit()
            #Pull parent thread and update recentreply attribute
            oppost = spBoard.query.get(parentthread)
            oppost.recentreply = newpost.postid
            db.session.commit()
            return redirect(url)
        except: 
            return "Failed to Post to Database"
    else:
        #Filter threads by given postid and replies by parentthread, and render
        chanthreads = spBoard.query.filter_by(postid=parentthread)
        childposts = spBoard.query.filter_by(parentthread=postid)
        return render_template('lynxthread.html', boardtitle=title, boarddesc=desc, url=url, boardurl=boardurl, chanthreads=chanthreads, childposts=childposts)


####################

#RS BOARD
@app.route('/rs/', methods=["POST", "GET"])
def research():
    title = "RESEARCH"
    desc = "ETERNAL BLADE"
    url = '/rs/'
    parentthread = 0

    #POST SEQUENCE - New Thread
    if request.method == "POST":
        post_username = request.form['username']
        post_subject = request.form['subject']
        post_message = request.form['message']
        if not post_username:
            post_username = 'Anonymous'
        if not post_subject:
            post_subject = '[No Subject]'

        #Parse Message String for Postlinks
        extracted_link = linkchecker(post_message)

        #Declare Database Object 
        newpost = rsBoard(post_username, post_subject, post_message, extracted_link, parentthread)

        #Attempt committing to DB and reload as GET
        try:
            #Add the new post
            db.session.add(newpost)
            db.session.commit()
            #Set new thread's recent reply to its own post ID so it bumps
            newpost.recentreply = newpost.postid
            db.session.commit()
            return redirect(url)
        except: 
            return "Failed to Post to Database"

    else:
        #GET method
        #Filter for Threads by descending bump
        chanthreads = rsBoard.query.filter(rsBoard.parentthread==0).order_by(rsBoard.recentreply.desc())

        #Pull each thread's recent reply into a list
        childposts = []
        for chanthread in chanthreads:
            tag = chanthread.recentreply
            childposts.append(rsBoard.query.get(tag))
        
        #Pass Parent and Child post lists into render function
        return render_template('lynxboard.html', boardtitle=title, boarddesc=desc, url=url, chanthreads=chanthreads, childposts=childposts)

@app.route('/rs/<int:postid>', methods=["POST", "GET"])
def researchthread(postid):
    title = "RESEARCH"
    desc = "ETERNAL BLADE"
    boardurl = '/rs/'
    url = '/rs/' + str(postid)
    threadnumber = rsBoard.query.get_or_404(postid)
    parentthread = postid

    #POST method - Reply to Thread <postid>
    if request.method == "POST":
        post_username = request.form['username']
        post_message = request.form['message']
        post_subject = 'Reply'
        if not post_username:
            post_username = 'Anonymous'

        #Parse Message String for Postlinks
        extracted_link = linkchecker(post_message)

        #Declare Database Object
        newpost = rsBoard(post_username, post_subject, post_message, extracted_link, parentthread)

        #Attempt committing to DB and reload as GET
        try:
            db.session.add(newpost)
            db.session.commit()
            #Pull parent thread and update recentreply attribute
            oppost = rsBoard.query.get(parentthread)
            oppost.recentreply = newpost.postid
            db.session.commit()
            return redirect(url)
        except: 
            return "Failed to Post to Database"
    else:
        #Filter threads by given postid and replies by parentthread, and render
        chanthreads = rsBoard.query.filter_by(postid=parentthread)
        childposts = rsBoard.query.filter_by(parentthread=postid)
        return render_template('lynxthread.html', boardtitle=title, boarddesc=desc, url=url, boardurl=boardurl, chanthreads=chanthreads, childposts=childposts)

####################

#LS BOARD
@app.route('/ls/', methods=["POST", "GET"])
def misc():
    title = "LAB MISC"
    desc = "DIGITAL REFUSE"
    url = '/ls/'
    parentthread = 0

    #POST SEQUENCE - New Thread
    if request.method == "POST":
        post_username = request.form['username']
        post_subject = request.form['subject']
        post_message = request.form['message']
        if not post_username:
            post_username = 'Anonymous'
        if not post_subject:
            post_subject = '[No Subject]'

        #Parse Message String for Postlinks
        extracted_link = linkchecker(post_message)

        #Declare Database Object 
        newpost = lsBoard(post_username, post_subject, post_message, extracted_link, parentthread)

        #Attempt committing to DB and reload as GET
        try:
            #Add the new post
            db.session.add(newpost)
            db.session.commit()
            #Set new thread's recent reply to its own post ID so it bumps
            newpost.recentreply = newpost.postid
            db.session.commit()
            return redirect(url)
        except: 
            return "Failed to Post to Database"

    else:
        #GET method
        #Filter for Threads by descending bump
        chanthreads = lsBoard.query.filter(lsBoard.parentthread==0).order_by(lsBoard.recentreply.desc())

        #Pull each thread's recent reply into a list
        childposts = []
        for chanthread in chanthreads:
            tag = chanthread.recentreply
            childposts.append(lsBoard.query.get(tag))
        
        #Pass Parent and Child post lists into render function
        return render_template('lynxboard.html', boardtitle=title, boarddesc=desc, url=url, chanthreads=chanthreads, childposts=childposts)

@app.route('/ls/<int:postid>', methods=["POST", "GET"])
def miscthread(postid):
    title = "LAB MISC"
    desc = "DIGITAL REFUSE"
    boardurl = '/ls/'
    url = '/ls/' + str(postid)
    threadnumber = lsBoard.query.get_or_404(postid)
    parentthread = postid

    #POST method - Reply to Thread <postid>
    if request.method == "POST":
        post_username = request.form['username']
        post_message = request.form['message']
        post_subject = 'Reply'
        if not post_username:
            post_username = 'Anonymous'

        #Parse Message String for Postlinks
        extracted_link = linkchecker(post_message)

        #Declare Database Object
        newpost = lsBoard(post_username, post_subject, post_message, extracted_link, parentthread)

        #Attempt committing to DB and reload as GET
        try:
            db.session.add(newpost)
            db.session.commit()
            #Pull parent thread and update recentreply attribute
            oppost = lsBoard.query.get(parentthread)
            oppost.recentreply = newpost.postid
            db.session.commit()
            return redirect(url)
        except: 
            return "Failed to Post to Database"
    else:
        #Filter threads by given postid and replies by parentthread, and render
        chanthreads = lsBoard.query.filter_by(postid=parentthread)
        childposts = lsBoard.query.filter_by(parentthread=postid)
        return render_template('lynxthread.html', boardtitle=title, boarddesc=desc, url=url, boardurl=boardurl, chanthreads=chanthreads, childposts=childposts)

####################

#PN BOARD
@app.route('/pn/', methods=["POST", "GET"])
def notes():
    title = "PROJECT NOTES"
    desc = "TOMBOY SUPREMACY"
    url = '/pn/'
    parentthread = 0

    #POST SEQUENCE - New Thread
    if request.method == "POST":
        post_username = request.form['username']
        post_subject = request.form['subject']
        post_message = request.form['message']
        if not post_username:
            post_username = 'Anonymous'
        if not post_subject:
            post_subject = '[No Subject]'

        #Parse Message String for Postlinks
        extracted_link = linkchecker(post_message)

        #Declare Database Object 
        newpost = pnBoard(post_username, post_subject, post_message, extracted_link, parentthread)

        #Attempt committing to DB and reload as GET
        try:
            #Add the new post
            db.session.add(newpost)
            db.session.commit()
            #Set new thread's recent reply to its own post ID so it bumps
            newpost.recentreply = newpost.postid
            db.session.commit()
            return redirect(url)
        except: 
            return "Failed to Post to Database"

    else:
        #GET method
        #Filter for Threads by descending bump
        chanthreads = pnBoard.query.filter(pnBoard.parentthread==0).order_by(pnBoard.recentreply.desc())

        #Pull each thread's recent reply into a list
        childposts = []
        for chanthread in chanthreads:
            tag = chanthread.recentreply
            childposts.append(pnBoard.query.get(tag))
        
        #Pass Parent and Child post lists into render function
        return render_template('lynxboard.html', boardtitle=title, boarddesc=desc, url=url, chanthreads=chanthreads, childposts=childposts)

@app.route('/pn/<int:postid>', methods=["POST", "GET"])
def notesthread(postid):
    title = "PROJECT NOTES"
    desc = "TOMBOY SUPREMACY"
    boardurl = '/pn/'
    url = '/pn/' + str(postid)
    threadnumber = pnBoard.query.get_or_404(postid)
    parentthread = postid

    #POST method - Reply to Thread <postid>
    if request.method == "POST":
        post_username = request.form['username']
        post_message = request.form['message']
        post_subject = 'Reply'
        if not post_username:
            post_username = 'Anonymous'

        #Parse Message String for Postlinks
        extracted_link = linkchecker(post_message)

        #Declare Database Object
        newpost = pnBoard(post_username, post_subject, post_message, extracted_link, parentthread)

        #Attempt committing to DB and reload as GET
        try:
            db.session.add(newpost)
            db.session.commit()
            #Pull parent thread and update recentreply attribute
            oppost = pnBoard.query.get(parentthread)
            oppost.recentreply = newpost.postid
            db.session.commit()
            return redirect(url)
        except: 
            return "Failed to Post to Database"
    else:
        #Filter threads by given postid and replies by parentthread, and render
        chanthreads = pnBoard.query.filter_by(postid=parentthread)
        childposts = pnBoard.query.filter_by(parentthread=postid)
        return render_template('lynxthread.html', boardtitle=title, boarddesc=desc, url=url, boardurl=boardurl, chanthreads=chanthreads, childposts=childposts)





#FLASK MAIN LOOP
if __name__ == '__main__':
    app.run()
