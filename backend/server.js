const express = require("express");
const sql = require("mssql");
const cors = require("cors");
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

// Configuración de SQL Server
const config = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  server: process.env.DB_SERVER,
  database: process.env.DB_DATABASE,
  port: parseInt(process.env.DB_PORT),
  options: {
    encrypt: false,
    trustServerCertificate: true,
  },
};

// Ruta para obtener bitácora
app.get("/api/bitacora", async (req, res) => {
  try {
    await sql.connect(config);
    const result = await sql.query(`
      SELECT sv.id, v.modelo, sv.fecha_salida, sv.kilometraje_salida, sv.condicion_salida,
             sv.fecha_entrada, sv.kilometraje_entrada, sv.condicion_entrada,
             sv.usuario, sv.departamento, sv.incidencia
      FROM SalidasVehiculos sv
      JOIN Vehiculos v ON sv.vehiculo_id = v.id
      ORDER BY sv.id DESC
    `);
    res.json(result.recordset);
  } catch (err) {
    console.error("Error en /api/bitacora", err);
    res.status(500).send("Error en el servidor");
  }
});

// Iniciar servidor
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
