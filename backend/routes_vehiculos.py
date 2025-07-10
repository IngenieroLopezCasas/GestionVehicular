from flask import Flask, request, jsonify
import pyodbc
from flask_cors import CORS

app = Flask(__name__)
# CORS(app)

DB_CONNECTION = "DRIVER={SQL Server};SERVER=DESKTOP-HT478MM;DATABASE=ControlVehicular;UID=UserCVehicular;PWD=V3h1cul9r"

def get_db_connection():
    return pyodbc.connect(DB_CONNECTION)


# -------------------- RUTAS CRUD --------------------

@app.route("/vehicles", methods=["GET"])
def get_vehicles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Vehiculos")
    rows = cursor.fetchall()
    columnas = [column[0] for column in cursor.description]
    vehicles = [dict(zip(columnas, row)) for row in rows]
    conn.close()
    return jsonify(vehicles)


@app.route("/vehicles", methods=["POST"])
def add_vehicle():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Vehiculos 
        (marca, modelo, placas, color, serie, unidad, transmision, iddepartamento, submarca, estatus, km)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["marca"], data["modelo"], data["placas"], data["color"], data["serie"],
        data["unidad"], data["transmision"], data["iddepartamento"], data["submarca"], data["estatus"], data.get("km", 0)
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Vehículo agregado correctamente"}), 201


@app.route("/vehicles/<int:id>", methods=["PUT"])
def update_vehicle(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Vehiculos
        SET marca=?, modelo=?, placas=?, color=?, serie=?, unidad=?, transmision=?, iddepartamento=?, submarca=?, estatus=?, km=?
        WHERE id=?
    """, (
        data["marca"], data["modelo"], data["placas"], data["color"], data["serie"],
        data["unidad"], data["transmision"], data["iddepartamento"], data["submarca"], data["estatus"], data.get("km", 0), id
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Vehículo actualizado correctamente"})


@app.route("/vehicles/<int:id>", methods=["DELETE"])
def delete_vehicle(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Vehiculos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Vehículo eliminado correctamente"})
