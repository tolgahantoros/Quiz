from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"

# Veritabanı başlatma
def init_db():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, username TEXT, score INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# En yüksek skoru veritabanından alma fonksiyonu
def get_high_score():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute("SELECT MAX(score) FROM scores")
    high_score = c.fetchone()[0]
    conn.close()
    return high_score if high_score else 0  # Eğer skor yoksa 0 döndürüyoruz

# Ana Sayfa
@app.route('/')
def index():
    high_score = get_high_score()  # En yüksek skoru alıyoruz
    return render_template('index.html', high_score=high_score)  # Skoru şablona gönderiyoruz

# Sınav Sayfası
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    high_score = get_high_score()  # En yüksek skoru alıyoruz
    if request.method == 'POST':
        username = request.form.get('username', 'Anonymous')
        answers = {
            "question1": request.form.get('question1', ''),
            "question2": request.form.get('question2', ''),
            "question3": request.form.get('question3', ''),
        }

        # Basit bir puanlama sistemi
        score = 0
        if answers["question1"] == "blue":
            score += 1
        if answers["question2"] == "dog":
            score += 1

        # Veritabanına kaydet
        conn = sqlite3.connect('quiz.db')
        c = conn.cursor()
        c.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (username, score))
        conn.commit()

        # En yüksek puanı bul
        c.execute("SELECT MAX(score) FROM scores")
        high_score = c.fetchone()[0]
        conn.close()

        session['score'] = score
        session['high_score'] = high_score

        return redirect(url_for('result', high_score=high_score))  # Skorla birlikte yönlendiriyoruz

    return render_template('quiz.html', high_score=high_score)  # Skoru şablona gönderiyoruz

# Sonuç Sayfası
@app.route('/result')
def result():
    score = session.get('score', 0)
    high_score = session.get('high_score', 0)
    return render_template('result.html', score=score, high_score=high_score)  # Skorları şablona gönderiyoruz

if __name__ == '__main__':
    app.run(debug=True)
