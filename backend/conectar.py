import pyodbc
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from datetime import datetime



app = Flask(__name__)
CORS(app)

DB_CONNECTION = "DRIVER={SQL Server};SERVER=DESKTOP-HT478MM;DATABASE=ControlVehicular;UID=UserCVehicular;PWD=V3h1cul9r"


def get_db_connection():
    return pyodbc.connect(DB_CONNECTION)

# # Función auxiliar
# def get_db_connection():
#     return pyodbc.connect(DB_CONNECTION)

# # Obtener todos los vehículos
# @app.route("/vehicles", methods=["GET"])
# def obtener_vehiculos():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM Vehiculos")
#     columnas = [column[0] for column in cursor.description]
#     resultados = [dict(zip(columnas, row)) for row in cursor.fetchall()]
#     conn.close()
#     return jsonify(resultados)

# # Actualizar un vehículo
# @app.route("/vehicles/<int:id>", methods=["PUT"])
# def update_vehicle(id):
#     data = request.json
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         UPDATE Vehiculos
#         SET marca=?, modelo=?, placas=?, color=?, serie=?, unidad=?, transmision=?, iddepartamento=?, submarca=?, estatus=?, km=?
#         WHERE IdVehiculos=?
#     """, (
#         data["marca"], data["modelo"], data["placas"], data["color"], data["serie"],
#         data["unidad"], data["transmision"], data["iddepartamento"], data["submarca"],
#         data["estatus"], data.get("km", 0), id
#     ))
#     conn.commit()
#     conn.close()
#     return jsonify({"mensaje": "Vehículo actualizado correctamente"})

# # Eliminar un vehículo
# @app.route("/vehicles/<int:id>", methods=["DELETE"])
# def delete_vehicle(id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM Vehiculos WHERE IdVehiculos = ?", (id,))
#     conn.commit()
#     conn.close()
#     return jsonify({"mensaje": "Vehículo eliminado correctamente"})




@app.route("/vehicles", methods=["GET"])
def get_vehicles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Vehiculos WHERE Estatus=1")
    rows = cursor.fetchall()
    columnas = [column[0] for column in cursor.description]
    vehicles = [dict(zip(columnas, row)) for row in rows]
    conn.close()
    return jsonify(vehicles)



@app.route("/vehicles/Agregar", methods=["POST"])
def add_vehicle():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Vehiculos 
        (marca, modelo, placas, color, serie, unidad, transmision, iddepartamento, submarca, estatus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["marca"], data["modelo"], data["placas"], data["color"], data["serie"],
        data["unidad"], data["transmision"], data["iddepartamento"], data["submarca"], 1
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Vehículo agregado correctamente"}), 201



@app.route("/vehicles/Actualizar/<int:id>", methods=["POST"])
def update_vehicle(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Vehiculos
        SET marca=?, modelo=?, placas=?, color=?, serie=?, unidad=?, transmision=?, iddepartamento=?, submarca=?, estatus=?
        WHERE IdVehiculos=?
    """, (
        data["marca"], data["modelo"], data["placas"], data["color"], data["serie"],
        data["unidad"], data["transmision"], data["iddepartamento"], data["submarca"], data["estatus"], id
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Vehículo actualizado correctamente"})


@app.route("/vehicles/entradas/<int:id>", methods=["GET"])
def verificar_entrada(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Vehiculos WHERE IdVehiculos = ?", (id,))
    row = cursor.fetchone()
    columnas = [column[0] for column in cursor.description]
    conn.close()

    if row:
        vehiculo = dict(zip(columnas, row))
        return jsonify({"status": "ok", "vehiculo": vehiculo}), 200
    else:
        return jsonify({"status": "error", "mensaje": "Vehículo no encontrado"}), 404




''''
@app.route("/vehicles/<int:id>", methods=["DELETE"])
def delete_vehicle(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Vehiculos WHERE IdVehiculos = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Vehículo eliminado correctamente"})

    '''
@app.route("/vehicles/baja/<int:id>", methods=["POST"])
def delete_vehicle(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Vehiculos SET Estatus = 0 WHERE IdVehiculos = ?", (id))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Vehículo dado de baja correctamente"})


@app.route("/usuarios", methods=["GET"])
def obtener_usuarios():
    conn = pyodbc.connect("DRIVER={SQL Server};SERVER=DESKTOP-HT478MM;DATABASE=IntranetCRT;UID=UserCVehicular;PWD=V3h1cul9r")
    cursor = conn.cursor()
    cursor.execute("SELECT IdUsuario, UserName, Nombre, ApellidoPat, ApellidoMat FROM IntranetCRT..NetUsuarios WHERE Activo = 1")
    usuarios = [
        {"IdUsuario": row[0], "UserName": row[1], "Nombre": row[2], "ApellidoPat": row[3], "ApellidoMat": row[4]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(usuarios)


@app.route("/vehicles/entradas", methods=["POST"])
def registrar_entrada():
    data = request.json
    print(data)
    user_id = data["idUsuario"]
    entrada_datetime = datetime.fromisoformat(data["fecha"])
    km = data["km"]
    tanque = data["gasolina"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        WITH CTE AS (
            SELECT TOP 1 *
            FROM Desplazamiento_2
            WHERE IdUsuario = ? AND Estatus = 0
            ORDER BY IdDesplazamiento DESC
        )
        UPDATE CTE
        SET Entrada = ?, KmEntrada = ?, TanqueEntrada = ?, Estatus = 1;
        """, (
        user_id,           # este es el primer ?, para el WHERE
        entrada_datetime,  # segundo ?, Entrada
        km,                # tercero ?, KmEntrada
        tanque             # cuarto ?, TanqueEntrada
    ))


    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "No se encontró ningún desplazamiento abierto para este usuario"}), 404

    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Entrada registrada correctamente"}), 200

@app.route("/vehicles/salida", methods=["POST"])
def registrar_salida():
    data = request.json
    print(data)

    salida_datetime = datetime.fromisoformat(data["salida"])
    idvehiculo = data.get("idvehiculo")
    if not idvehiculo:
        return jsonify({"error": "Falta el ID del vehículo"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Desplazamiento_2 (Salida, KmSalida, TanqueSalida, IdUsuario,IdVehiculo ,Estatus)
        VALUES (?, ?, ?, ?, ?,0)
    """, (
        salida_datetime,
        data["kmSalida"],
        data["tanqueSalida"],
        data["idUsuario"],
        idvehiculo    
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Salida registrada correctamente"}), 200

@app.route("/vehicles/ultimos-datos/<int:idvehiculo>", methods=["GET"])
def obtener_ultima_entrada(idvehiculo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 1 KmEntrada, TanqueEntrada
        FROM Desplazamiento_2
        WHERE IdVehiculo = ? AND Estatus = 1
        ORDER BY IdDesplazamiento DESC
    """, (idvehiculo,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            "km": row[0],
            "gasolina": row[1]
        })
    else:
        return jsonify({"km": 0, "gasolina": 0})  # Si no hay registros anteriores
'''''
@app.route("/vehicles/mostrar-vehiculos", methods=["GET"])
def mostrar():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Desplazamiento_2")
    rows = cursor.fetchall()
    columnas = [column[0] for column in cursor.description]
    vehicles = [dict(zip(columnas, row)) for row in rows]
    conn.close()
    return jsonify(vehicles)
'''


@app.route("/checklist", methods=["POST"])
def crear_checklist():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    entrada_datetime = datetime.fromisoformat(data["Fecha"])  # ✅ CORREGIDO

    print(data)
    cursor.execute("""
        INSERT INTO CheckList_2 (IdVehiculo, Fecha, IdUsuarioEntrega, IdUsuarioRecibe, IdEvento)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["IdVehiculo"],
        entrada_datetime,
        data["IdUsuarioEntrega"],
        data["IdUsuarioRecibe"],
        data["IdEvento"]
    ))

    cursor.execute("SELECT SCOPE_IDENTITY()")
    id_checklist = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Checklist creado", "IdCheckList": id_checklist}), 200


@app.route("/checklist/accesorios", methods=["POST"])
def guardar_accesorios():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Convertir booleanos a 0/1
    accesorios = {k: int(v) for k, v in data.items() if k != "IdCheckList"}

    cursor.execute("""
        INSERT INTO Accesorios (
            Luces, Direccionales, Intermitentes, Cuartos, LuzdeFreno,
            LuzdeReversa, LuzInterior, LuzTablero, Bocinas, Reloj, Tapetes,
            Aire, Claxon, Limpiadores, Encendedor, Estereo, ElevedordeCristal,
            LlantaRefacion, GatoyLlave, Herramienta, TaponesPolveras, Extintor,
            IdCheckList
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        accesorios["Luces"], accesorios["Direccionales"], accesorios["Intermitentes"],
        accesorios["Cuartos"], accesorios["LuzdeFreno"], accesorios["LuzdeReversa"],
        accesorios["LuzInterior"], accesorios["LuzTablero"], accesorios["Bocinas"],
        accesorios["Reloj"], accesorios["Tapetes"], accesorios["Aire"],
        accesorios["Claxon"], accesorios["Limpiadores"], accesorios["Encendedor"],
        accesorios["Estereo"], accesorios["ElevedordeCristal"], accesorios["LlantaRefacion"],
        accesorios["GatoyLlave"], accesorios["Herramienta"], accesorios["TaponesPolveras"],
        accesorios["Extintor"], int(data["IdCheckList"])
    ))

    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Accesorios registrados"}), 200

@app.route("/vehicles/por-qr/<qr_code>", methods=["GET"])
def obtener_vehiculo_por_qr(qr_code):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Vehiculos WHERE QR = ?", (qr_code,))
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            vehiculo = dict(zip(columns, row))
            return jsonify({"status": "ok", "vehiculo": vehiculo})
        else:
            return jsonify({"status": "error", "message": "Vehículo no encontrado"}), 404
    except Exception as e:
        print("Error en consulta por QR:", e)
        return jsonify({"status": "error", "message": "Error interno"}), 500

@app.route("/vehicles/historial/<int:idvehiculo>", methods=["GET"])
def historial_vehiculo(idvehiculo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 10 Salida, Entrada, KmSalida, KmEntrada, TanqueSalida, TanqueEntrada
        FROM Desplazamiento_2
        WHERE IdVehiculo = ?
        ORDER BY IdDesplazamiento DESC
    """, (idvehiculo,))
    rows = cursor.fetchall()
    columnas = [column[0] for column in cursor.description]
    desplazamientos = [dict(zip(columnas, row)) for row in rows]
    conn.close()
    return jsonify(desplazamientos)


# Iniciar servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
