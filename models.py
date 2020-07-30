from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Usuarios(db.Model):
	__tablename__ = "Usuarios"
	DNI = db.Column(db.Integer, primary_key=True)
	Clave = db.Column(db.String(120), nullable=False)
	Tipo = db.Column(db.String(10), nullable=False)
	pedido = db.relationship('Pedidos', backref='mozo', cascade="all, delete-orphan", lazy='dynamic')

class Productos(db.Model):
	__tablename__ = "Productos"
	NumProducto = db.Column(db.Integer, primary_key=True)
	Nombre = db.Column(db.String(80), nullable=False)
	PrecioUnitario = db.Column(db.Float, nullable=False)
	items = db.relationship('ItemsPedidos', backref='producto', cascade="all, delete-orphan", lazy='dynamic')

class Pedidos(db.Model):
	__tablename__ = "Pedidos"
	NumPedido = db.Column(db.Integer, primary_key=True)
	Fecha = db.Column(db.DateTime, nullable=False)
	Total = db.Column(db.Float, nullable=False)
	Cobrado = db.Column(db.String(10), nullable=False)
	Observacion = db.Column(db.Text)
	DNIMozo = db.Column(db.Integer, db.ForeignKey('Usuarios.DNI'))
	Mesa = db.Column(db.Integer, nullable=False)
	items = db.relationship('ItemsPedidos', backref='pedido', cascade="all, delete-orphan", lazy='dynamic')

class ItemsPedidos(db.Model):
	__tablename__= 'ItemsPedidos'
	NumItem = db.Column(db.Integer, primary_key=True)
	NumPedido = db.Column(db.Integer, db.ForeignKey('Pedidos.NumPedido'))
	NumProducto = db.Column(db.Integer, db.ForeignKey('Productos.NumProducto'))
	Precio = db.Column(db.Float, nullable=False)
	Estado = db.Column(db.String(10), nullable=False)
