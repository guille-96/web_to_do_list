from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
import locale

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    fecha = db.Column(db.Date, nullable=False)
    completada = db.Column(db.Boolean, default=False, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    fecha_hoy = date.today()
    tareas = Tarea.query.filter(Tarea.fecha <= fecha_hoy, Tarea.completada == False).all()
    return render_template('homepage.html', tareas=tareas, fecha_hoy=fecha_hoy)

@app.route('/add', methods=['POST'])
def add():
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    fecha_str = request.form.get('fecha')

    if not titulo or not fecha_str:
        return jsonify(error="Título y fecha son obligatorios"), 400

    try:
        nueva_fecha = date.fromisoformat(fecha_str)
    except Exception:
        return jsonify(error="Fecha inválida, use formato YYYY-MM-DD"), 400

    nueva_tarea = Tarea(
        titulo=titulo,
        descripcion=descripcion,
        fecha=nueva_fecha,
        completada=False
    )

    try:
        db.session.add(nueva_tarea)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

@app.route('/update/<int:tarea_id>', methods=['POST'])
def update(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)

    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    fecha_str = request.form.get('fecha')

    if titulo:
        tarea.titulo = titulo
    if descripcion is not None:
        tarea.descripcion = descripcion
    if fecha_str:
        try:
            tarea.fecha = date.fromisoformat(fecha_str)
        except Exception:
            return jsonify(error="Fecha inválida, use formato YYYY-MM-DD"), 400

    try:
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

@app.route('/complete/<int:tarea_id>', methods=['POST'])
def complete(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    tarea.completada = True
    try:
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

@app.route('/calendar')
def calendar_view():
    view_mode = request.args.get('view', 'day')  # 'day', 'week', 'month'
    fecha_str = request.args.get('date')
    if fecha_str:
        fecha_actual = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    else:
        fecha_actual = date.today()

    if view_mode == 'day':
        tareas = Tarea.query.filter(Tarea.fecha == fecha_actual, Tarea.completada == False).all()
        fecha_inicio = fecha_actual
        fecha_fin = fecha_actual
    elif view_mode == 'week':
        start_of_week = fecha_actual - timedelta(days=fecha_actual.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        tareas = Tarea.query.filter(Tarea.fecha >= start_of_week,
                                    Tarea.fecha <= end_of_week,
                                    Tarea.completada == False).all()
        fecha_inicio = start_of_week
        fecha_fin = end_of_week
    else:  # month
        start_of_month = fecha_actual.replace(day=1)
        if fecha_actual.month == 12:
            next_month = fecha_actual.replace(year=fecha_actual.year + 1, month=1, day=1)
        else:
            next_month = fecha_actual.replace(month=fecha_actual.month + 1, day=1)
        end_of_month = next_month - timedelta(days=1)
        tareas = Tarea.query.filter(Tarea.fecha >= start_of_month,
                                    Tarea.fecha <= end_of_month,
                                    Tarea.completada == False).all()
        fecha_inicio = start_of_month
        fecha_fin = end_of_month

    return render_template(
        'calendar.html',
        tareas=tareas,
        view_mode=view_mode,
        fecha_actual=fecha_actual,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        timedelta = timedelta
    )


@app.route('/completadas')
def completadas_view():
    view_mode = request.args.get('view', 'day')
    fecha_str = request.args.get('date')
    if fecha_str:
        fecha_actual = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    else:
        fecha_actual = date.today()

    if view_mode == 'day':
        tareas = Tarea.query.filter(Tarea.fecha == fecha_actual, Tarea.completada == True).all()
        fecha_inicio = fecha_actual
        fecha_fin = fecha_actual
    elif view_mode == 'week':
        start_of_week = fecha_actual - timedelta(days=fecha_actual.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        tareas = Tarea.query.filter(Tarea.fecha >= start_of_week,
                                    Tarea.fecha <= end_of_week,
                                    Tarea.completada == True).all()
        fecha_inicio = start_of_week
        fecha_fin = end_of_week
    else:  # month
        start_of_month = fecha_actual.replace(day=1)
        if fecha_actual.month == 12:
            next_month = fecha_actual.replace(year=fecha_actual.year + 1, month=1, day=1)
        else:
            next_month = fecha_actual.replace(month=fecha_actual.month + 1, day=1)
        end_of_month = next_month - timedelta(days=1)
        tareas = Tarea.query.filter(Tarea.fecha >= start_of_month,
                                    Tarea.fecha <= end_of_month,
                                    Tarea.completada == True).all()
        fecha_inicio = start_of_month
        fecha_fin = end_of_month

    return render_template(
        'completadas.html',
        tareas=tareas,
        view_mode=view_mode,
        fecha_actual=fecha_actual,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        timedelta=timedelta
    )



if __name__ == '__main__':
    app.run(debug=True)
