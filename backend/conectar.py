import pyodbc
import traceback  # al inicio del archivo
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from datetime import datetime
import os
import time  
from werkzeug.utils import secure_filename  # ✅ Importación necesaria

app = Flask(__name__)
UPLOAD_FOLDER = r"D:\JuanFrancisco\backend\uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER




# Crear carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



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
        SELECT TOP 2 IdDesplazamiento, Salida, Entrada, KmSalida, KmEntrada, TanqueSalida, TanqueEntrada
        FROM Desplazamiento_2
        WHERE IdVehiculo = ?
        ORDER BY IdDesplazamiento DESC
    """, (idvehiculo,))
    rows = cursor.fetchall()
    columnas = [column[0] for column in cursor.description]
    desplazamientos = [dict(zip(columnas, row)) for row in rows]
    conn.close()
    return jsonify(desplazamientos)
'''
@app.route("/subir-imagen", methods=["POST"])
def subir_imagen():
    if "imagenes" not in request.files:
        return jsonify({"error": "No se encontraron archivos"}), 400

    archivos = request.files.getlist("imagenes")
    allowed_ext = {"png", "jpg", "jpeg", "gif"}

    upload_folder = "uploads"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    nombres_guardados = []

    for archivo in archivos:
        if archivo.filename == "":
            continue

        # Asegurarse que el archivo tiene extensión
        if "." not in archivo.filename:
            continue

        ext = archivo.filename.rsplit(".", 1)[1].lower()
        if ext not in allowed_ext:
            continue

        filename = secure_filename(archivo.filename)
        save_path = os.path.join(upload_folder, filename)

        # Evitar sobrescribir archivos existentes
        count = 1
        base, extension = os.path.splitext(filename)
        while os.path.exists(save_path):
            filename = f"{base}_{count}{extension}"
            save_path = os.path.join(upload_folder, filename)
            count += 1

        archivo.save(save_path)
        nombres_guardados.append(filename)

    if not nombres_guardados:
        return jsonify({"error": "No se subieron archivos válidos"}), 400

    return jsonify({"mensaje": "Imágenes subidas correctamente", "nombres": nombres_guardados}), 201
'''


@app.route("/evento/agregar", methods=["POST"])
def agregar_evento():
    data = request.json
    print("Datos recibidos en /evento/agregar:", data)
    observacion = data.get("Observacion")
    id_desplazamiento = data.get("IdDesplazamiento")

    if not observacion or id_desplazamiento is None:
        print("❌ Faltan datos requeridos")
        return jsonify({"error": "Faltan datos requeridos"}), 400

    try:
        id_desplazamiento_int = int(id_desplazamiento)
    except (ValueError, TypeError):
        print("❌ IdDesplazamiento inválido")
        return jsonify({"error": "IdDesplazamiento debe ser un entero válido"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            EXEC ControlVehicular.dbo.CV_InsertarEvento 
                @Observacion = ?, 
                @IdDesplazamiento = ?
        """, (observacion, id_desplazamiento_int))

        cursor.nextset()  # <<< Añadido aquí

        row = cursor.fetchone()
        if not row:
            raise Exception("No se devolvió ningún ID desde el procedimiento.")

        id_evento = int(row[0])

        # Confirmar transacción
        conn.commit()

        print(f"✅ Evento insertado con ID: {id_evento}")
        conn.close()

        return jsonify({
            "mensaje": "Evento agregado correctamente",
            "IdEvento": id_evento
        }), 201

    except Exception as e:
        conn.rollback()
        conn.close()
        print("❌ Error al agregar evento:")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Error interno al agregar evento"
        }), 500





@app.route("/upload-image", methods=["POST"])
def upload_images():
    if "imagenes" not in request.files:
        return jsonify({"error": "No se encontraron archivos"}), 400

    archivos = request.files.getlist("imagenes")
    allowed_ext = {"png", "jpg", "jpeg", "gif"}

    import os
    from werkzeug.utils import secure_filename

    upload_folder = "uploads"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    nombres_guardados = []

    for archivo in archivos:
        if archivo.filename == "":
            continue
        ext = archivo.filename.rsplit(".", 1)[1].lower()
        if ext not in allowed_ext:
            continue
        filename = secure_filename(archivo.filename)
        save_path = os.path.join(upload_folder, filename)

        # Evitar duplicados
        count = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(save_path):
            filename = f"{base}_{count}{ext}"
            save_path = os.path.join(upload_folder, filename)
            count += 1

        archivo.save(save_path)
        nombres_guardados.append(filename)

    if not nombres_guardados:
        return jsonify({"error": "No se subieron archivos válidos"}), 400

    return jsonify({"mensaje": "Imágenes subidas correctamente", "nombres": nombres_guardados}), 201
'''
@app.route('/agregar/roles/<int:id_usuario>', methods=['POST'])
def agregar_rol(id_usuario):
    data=request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        INSERT INTO Roles
        (idusuario,rol,status)
        VALUES (?,?,?)

""", (
    id_usuario,data["rol"],data["status"]
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "ROl asignado"}), 201
        
'''




@app.route('/desplazamientos/ultimo/<int:id_vehiculo>', methods=['GET'])
def obtener_ultimo_desplazamiento(id_vehiculo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 1 IdDesplazamiento
        FROM Desplazamiento_2
        WHERE IdVehiculo = ?
        ORDER BY IdDesplazamiento DESC
    """, id_vehiculo)
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({'IdDesplazamiento': row.IdDesplazamiento})
    else:
        return jsonify({'error': 'No se encontró desplazamiento'}), 404

@app.route('/fotos/agregar', methods=['POST'])
def agregar_fotos():
    try:
        archivos = request.files.getlist('fotos')
        if not archivos:
            return jsonify({'error': 'No se encontraron archivos con la clave "fotos"'}), 400

        idEvento = request.form.get('idEvento')
        if not idEvento:
            return jsonify({'error': 'idEvento es obligatorio'}), 400


        print(idEvento)
        print(archivos)
        conn = get_db_connection()
        cursor = conn.cursor()

        for idx, archivo in enumerate(archivos):
            # if archivo.filename == '':
            #     continue

            nombre_archivo = f"foto_{int(time.time())}_{idx}.png"
            print(nombre_archivo)
            ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
            print(ruta_archivo)
            archivo.save(ruta_archivo)

            # Solo guardar el nombre del archivo, no la ruta completa
            cursor.execute("INSERT INTO Fotos (idEvento, Imagen) VALUES (?, ?)", (idEvento, nombre_archivo))

        conn.commit()
        # cursor.close()
        conn.close()

        return jsonify({'mensaje': 'Fotos subidas correctamente'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al subir fotos: {str(e)}'}), 500



#endpoint para revisar rol en loggin
@app.route('/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Faltan credenciales'}), 400

    try:
        conn = pyodbc.connect("DRIVER={SQL Server};SERVER=DESKTOP-HT478MM;DATABASE=IntranetCRT;UID=UserCVehicular;PWD=V3h1cul9r")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.IdUsuario, u.Nombre, u.UserName, u.UsuarioInterno, r.Rol
            FROM IntranetCRT..NetUsuarios u
            LEFT JOIN ControlVehicular.dbo.Roles r ON u.IdUsuario = r.IdUsuario AND r.Status = 1
            WHERE u.UserName = ? AND u.Password = ? AND u.Activo = 1
        """, (username, password))

        row = cursor.fetchone()
        if not row:
            return jsonify({'result': {'success': False, 'message': 'Credenciales incorrectas'}}), 401

        usuario = {
            'idUsuario': row.IdUsuario,
            'nombre': row.Nombre,
            'usuarioInterno': row.UsuarioInterno,
            'rol': row.Rol or 'usuario'  # Si no tiene rol asignado, se le da uno genérico
        }

        return jsonify({'result': {'success': True, 'user': usuario}})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500

    finally:
        conn.close()
@app.route('/agregar/roles/<int:id_usuario>', methods=['POST'])
def agregar_rol(id_usuario):
    data = request.json
    rol = data.get('rol')
    status = data.get('status', 1)

    if not rol:
        return jsonify({'error': 'Falta el rol'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Roles (idusuario, rol, status)
            VALUES (?, ?, ?)
            """, (id_usuario, rol, status))
        conn.commit()
        return jsonify({'mensaje': 'Rol asignado correctamente'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()




# Iniciar servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
