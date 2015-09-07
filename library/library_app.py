import os

from flask import Flask, g, render_template, request

import sqlite3

app = Flask(__name__)
display = 'none'

def connect_db():
    return sqlite3.connect('database.db')

@app.before_request
def before_request():
    g.db = connect_db()

@app.route('/', methods=['POST','GET'])
def hello_world():
    if request.method == 'GET':
        library_name = 'the Universal'
        return render_template('index.html', library_name=library_name)
    elif request.method == 'POST':
        c = g.db.execute('SELECT * FROM book WHERE title LIKE (?)',(request.form['search'],))
        results = c.fetchall()
        title = "Search Results"
        if results:
            return render_template('search_results.html', results=results, title=title)
        else:
            title = 'Oops!'
            message = 'That entry doesn\'t exist!'
            buttontext = 'Add Entry'
            display = 'initial'
            path = 'add'
            return render_template('landingpage.html', title=title, message=message, display=display, buttontext=buttontext, path=path)
            
@app.route('/add', methods=['POST','GET'])
def add():
    title = 'Add a Book to the Library'
    if request.method == 'GET':
        return render_template('add.html', title=title)
    elif request.method == 'POST':
        # take info from form, insert into tuple, into db, then commit
        t = (int(request.form['author']), str(request.form['title']), str(request.form['isbn']))
        g.db.execute('INSERT INTO book (author_id, title, isbn) VALUES (?,?,?);', t)
        g.db.commit()
        title = "Thank You"
        message = "Submitted title: {}".format(request.form['title'])
        return render_template('landingpage.html', title = title, message=message, display=display)
    

@app.route('/viewlibrary')
def viewlibrary():
    c = g.db.execute('SELECT * FROM book;')
    book_values = c.fetchall()
    books = []
    for each in book_values:
        book = {}
        book['id'] = each[0]
        a = g.db.execute('SELECT name FROM author WHERE id=?',(each[1],))
        author = a.fetchone()
        book['author'] = author[0]
        book['title'] = each[2]
        book['isbn'] = each[3]
        books.append(book)
    title = "Library"
    return render_template('view.html', books=books, title=title)
    
    
@app.route('/book/<int:book_id>', methods=['POST','GET'])
def view_book(book_id):
    if request.method == 'GET':
        c = g.db.execute('SELECT title, isbn, author_id FROM book WHERE id=(?);', (int(book_id), ))
        book_list = c.fetchone()
        d = g.db.execute('SELECT name FROM author WHERE id=(?);', (int(book_list[2]),))
        author_list = d.fetchone()
        book = { 'title': book_list[0], 'isbn': book_list[1], 'author': author_list[0]}
        return render_template('book.html', book=book)
    elif request.method == 'POST':
        
        if request.form['delete'] and request.form['delete'] == 'yes':
            g.db.execute('DELETE FROM book WHERE id=?',(int(book_id),))
            g.db.commit()
            title = "Success"
            message = "Entry deleted!"
            return render_template('landingpage.html', title=title, message=message, display=display) 
        else:
            g.db.execute('UPDATE book SET author_id=:author_id, \
                      title=:title, isbn=:isbn WHERE id=:id;', \
                      {'author_id': int(request.form['author']),
                       'title': request.form['title'],
                       'isbn': request.form['isbn'],
                       'id': int(book_id)
                       }
                       )
        g.db.commit()
        title = "Success"
        message = "Entry updated!"
        display = 'initial'
        path = "book/{}".format(book_id)
        buttontext = 'See updated entry'
        return render_template('landingpage.html', title=title, message=message,display=display,path=path, buttontext=buttontext) 
    

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
