# =========================
# =     importaciones     =
# =========================
import sys
import mysql.connector
from datetime import datetime
from fpdf import FPDF
from PyQt5 import uic, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi(r'ui.ui', self)
        self.fnUI()
        self.fnData()
        
    
    # ==> Conexión de botones con sus funciones <==
    def fnUI(self):
        self.btnActualizar.setEnabled(False)
        self.btnRegistrar.setEnabled(False)
        
        self.btnActualizar.clicked.connect(self.fnActualizar)
        self.btnAplicar.clicked.connect(self.fnActivador)
        self.btnBuscar.clicked.connect(self.fnConsultar)
        self.btnEliminar.clicked.connect(self.fnEliminar)
        self.btnLimpiar.clicked.connect(self.fnLimpiar)
        self.btnRegistrar.clicked.connect(self.fnRegistrar)
        self.btnReporte.clicked.connect(self.fnReporte)


    # ==>   CARGA DE TABLA CON LOS DATOS <==
    def fnData(self):
        con = mysql.connector.connect(
            host     = 'localhost',
            user     = 'root',
            password = 'admin',
            database = 'registros'
        )
        c = con.cursor()
        sql = '''
            SELECT * FROM alumnos;
        '''
        c.execute(sql)
        registros = c.fetchall()

        for registro in registros:
            fila = self.tbwTabla.rowCount()
            self.tbwTabla.insertRow(fila)

            for i in range(len(registro)):
                dato = registro[i]
                self.tbwTabla.setItem(fila, i, QTableWidgetItem(str(dato)))
        
        self.becados()
        

    # ==>   Activación de botones según la acción <==
    def fnActivador(self):
        if self.cmbAccion.currentIndex() == 0:
            self.btnRegistrar.setEnabled(True)
            self.btnActualizar.setEnabled(False)
        elif self.cmbAccion.currentIndex() == 1:
            self.btnRegistrar.setEnabled(False)
            self.btnActualizar.setEnabled(True)
        else:
            self.btnActualizar.setEnabled(False)
            self.btnRegistrar.setEnabled(False)

    # ===============================
    # ==>   Registro de alumnos   <==
    # ===============================
    def fnRegistrar(self):
        data = self.datos()

        con = mysql.connector.connect(
            host     = 'localhost',
            user     = 'root',
            password = 'admin',
            database = 'Registros'
        )
        c = con.cursor()
        sql = '''
        INSERT INTO alumnos (matricula, nombre, paterno, materno, sexo, edad, direccion, municipio, estado, carrera, beca, materias)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        
        valores = (
            int(data[0]),
            str(data[1]),
            str(data[2]),
            str(data[3]),
            int(data[4]),
            int(data[5]),
            str(data[6]),
            str(data[7]),
            str(data[8]),
            str(data[9]),
            int(data[10]),
            str(data[11])
        )
        c.execute(sql, valores)
        con.commit()

        reg = self.tbwTabla.rowCount()
        self.tbwTabla.insertRow(reg)

        for i in range(len(data)):
            dato = data[i]
            self.tbwTabla.setItem(reg, i, QTableWidgetItem(str(dato)))
        
        beca = self.t_beca(data[10])
        msj = f'''
            === Alumno registrado correctamente ===
            
            --> Datos personales
            {data[0]} - {data[2]} {data[3]} {data[1]}
            Sexo: {"Maculino" if data[4] == 1 else "Femenino"}     Edad: {data[5]}

            --> Dirección:
            {data[6]}, {data[7]}, {data[8]}

            --> Datos académicos:
            Carrera: {data[9]}
            Beca: {beca}%
            Materias: {data[11]}
        '''
        self.txtPantalla.clear()
        self.txtPantalla.append(msj)

        self.becados()


    # ====================================
    # ==>   Actualización de alumnos   <==
    # ====================================
    def fnActualizar(self):
        # **Datos recibidos de los componentes
        data = self.datos()
        # **Datos obtenidos de la BD
        info = self.fnConsultar()

        con = mysql.connector.connect(
            host     = 'localhost',
            user     = 'root',
            password = 'admin',
            database = 'Registros'
        )
        c = con.cursor()
        sql = '''
            UPDATE alumnos SET
            nombre = %s, paterno = %s, materno = %s,
            sexo = %s, edad = %s,
            direccion = %s, municipio = %s, estado = %s,
            carrera = %s, beca = %s, materias = %s;
        '''
        valores = (data[1], data[2], data[3],
                   data[4], data[5], data[6],
                   data[7], data[8], data[9],
                   data[10], data[11] if len(data[11]) != '' else info[0][11])
        c.execute(sql, valores)
        con.commit()


    # ===============================
    # ==>   Consulta de alumnos   <==
    # ===============================
    def fnConsultar(self):
        matricula = (int(self.txtMatricula.text()),)
        
        con = mysql.connector.connect(
            host     = 'localhost',
            user     = 'root',
            password = 'admin',
            database = 'Registros'
        )
        c = con.cursor()
        sql = '''
            SELECT * FROM alumnos
            WHERE matricula = %s
        '''
        c.execute(sql, matricula)
        retorno = c.fetchall()

        # ** Evaluamos si la consulta devolvió un registro
        if len(retorno) > 0:
            # **Evaluamos el tipo de acción (Registrar o Actualizar)
            if not self.cmbAccion.currentIndex() == 1:
                beca = self.t_beca(retorno[0][10])
                msj = f'''
                    === RESULTADO DE LA BÚSQUEDA ===

                    -> Alumno
                    {retorno[0][0]} - {retorno[0][2]} {retorno[0][3]} {retorno[0][1]}
                    Sexo: {"Masculino" if retorno[0][4] == 1 else "Fememnino"}     Edad: {retorno[0][5]}
                    
                    -> Dirección
                    {retorno[0][6]}, {retorno[0][7]}, {retorno[0][8]}

                    -> Datos académicos
                    Carrera: {retorno[0][9]}
                    Beca: {beca}
                    Materías favoritas: {retorno[0][11]}
                '''
            else:
                # ** Si se va a actualizar se llenan los componentes
                self.txtNombre.setText(retorno[0][1])
                self.txtPaterno.setText(retorno[0][2])
                self.txtMaterno.setText(retorno[0][3])
                self.rdbMasculino.setChecked(True) if retorno[0][4] else self.rdbFemenino.setChecked(True)
                self.txtEdad.setText(str(retorno[0][5]))
                self.txtDireccion.setText(retorno[0][6])
                self.txtMunicipio.setText(retorno[0][7])
                estado = self.cmbEstado.findText(retorno[0][8])
                carrera = self.cmbCarrera.findText(retorno[0][9])
                self.cmbEstado.setCurrentIndex(estado)
                self.cmbCarrera.setCurrentIndex(carrera)
                
                if retorno[0][10] == 1:
                    self.rdb100.setChecked(True)
                elif retorno[0][10] == 2:
                    self.rdb80.setChecked(True)
                elif retorno[0][10] == 3:
                    self.rdb50.setChecked(True)
                else:
                    self.rdbNA.setChecked(True)
                
                msj = ''
                return retorno
        else:
            # ** Si consulta es vacia notificamos al usuario
            msj = f'''
                \tNo se encontró el alumno especificado
            '''

        self.txtPantalla.clear()
        self.txtPantalla.append(msj)


    # ====================================
    # ==>   Eliminación de un alumno   <==
    # ====================================
    def fnEliminar(self):
        # ** Recuperamos la fila seleccionada de la tabla
        registro = self.tbwTabla.currentRow()
        # ** Obtenemos la matrícula del alumno seleccionado
        b_mat = int(self.tbwTabla.item(registro, 0).text())
        
        con = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'admin',
            database = 'registros'
        )
        c = con.cursor()
        sql = f'''
            DELETE FROM alumnos
            WHERE matricula = {b_mat};
        '''
        c.execute(sql)
        con.commit()

        # ** Evaluamos si se encontró al alumno seleccionado
        if c.rowcount > 0:
            # ** Removemos al alumno de la tabla
            self.tbwTabla.removeRow(registro)
            msj = f'\tAlumno "{b_mat}" eliminado correctamente.'
        else:
            # ** Si no se encuentra se notifica al usuario
            msj = f'\tNo se encontró alumno especificado.'
        
        self.txtPantalla.clear()
        self.txtPantalla.append(msj)
        

    # ====================================
    # ==>   Reporte de un alumno   <==
    # ====================================
    def fnReporte(self):
        con = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'admin',
            database = 'registros'
        )
        c = con.cursor()
        sql = '''
        SELECT * FROM alumnos
        ORDER BY carrera;
        '''
        c.execute(sql)
        data = c.fetchall()

        carreras = [
            'Licenciado en Administración',
            'Licenciado en Contador Público',
            'Licenciado en Gestión de la Responsabilidad Social',
            'Licenciado en Negocios Internacionales',
            'Licenciado en Tecnologías de Información'
        ]

        la   = []
        lcp  = []
        lgrs = []
        lni  = []
        lti  = []

        for i in range(len(data)):
            alumno = data[i]
            if alumno[9] == carreras[0]:
                la.append(alumno)
            elif alumno[9] == carreras[1]:
                lcp.append(alumno)
            elif alumno[9] == carreras[2]:
                lgrs.append(alumno)
            elif alumno[9] == carreras[3]:
                lni.append(alumno)
            elif alumno[9] == carreras[4]:
                lti.append(alumno)
        
        alumnos_la = self.impresion(la)
        alumnos_lcp = self.impresion(lcp)
        alumnos_lgrs = self.impresion(lgrs)
        alumnos_lni = self.impresion(lni)
        alumnos_lti = self.impresion(lti)

        f = f'''
        REPORTE DE ALUMNOS
        Fecha: {datetime.today().strftime("%Y-%m-%d")}

        --> {carreras[0]}:{alumnos_la}\n
        --> {carreras[1]}:{alumnos_lcp}\n
        --> {carreras[2]}:{alumnos_lgrs}\n
        --> {carreras[3]}:{alumnos_lni}\n
        --> {carreras[4]}:{alumnos_lti}\n
        '''
        
        archivo = open('Reporte.txt', 'w')
        archivo.write(f)
        archivo.close()
        
        archivo = open('Reporte.txt', 'r')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', size = 9)
        line = 1

        for linea in archivo:
            pdf.cell(200, 7, txt = linea, ln = line, align = 'L')
            if linea[-1] == ('\n'):
                linea == linea[:-1]
            line += 1
        
        pdf.output(f'Reporte {datetime.today().strftime("%Y-%m-%d")}.pdf')
        archivo.close()

    
    def impresion(self, alumnos):
        listado = ''
        for alumno in alumnos:
            listado += f'''
            {alumno[0]} - {alumno[2]} {alumno[3]} {alumno[1]}'''
        return listado


    # ===================
    # =    Funciones    =
    # ===================

    # ===>   Obtención de datos <===
    def datos(self):
        matricula = self.txtMatricula.text()
        nombre    = self.txtNombre.text()
        paterno   = self.txtPaterno.text()
        materno   = self.txtMaterno.text()
        sexo      = self.sexo()
        edad      = self.txtEdad.text()
        direccion = self.txtDireccion.text()
        municipio = self.txtMunicipio.text()
        estado    = self.cmbEstado.currentText()
        carrera   = self.cmbCarrera.currentText()
        beca      = self.beca()
        materias  = self.materias()

        data = [matricula, nombre, paterno, materno, sexo, edad, direccion, municipio, estado, carrera, beca, materias]
        return data
        

    # ===> Limpiar campos <===
    def fnLimpiar(self):
        self.txtMatricula.clear()
        self.txtNombre.clear()
        self.txtPaterno.clear()
        self.txtMaterno.clear()
        self.rdbMasculino.setChecked(True)
        self.txtEdad.clear()
        self.txtDireccion.clear()
        self.txtMunicipio.clear()
        self.cmbEstado.setCurrentIndex(-1)
        self.cmbCarrera.setCurrentIndex(-1)
        self.rdbNA.setChecked(True)
        self.ckbContabilidad.setChecked(False)
        self.ckbProgramacion.setChecked(False)
        self.ckbBD.setChecked(False)
        self.ckbOperaciones.setChecked(False)
        self.ckbEstadistica.setChecked(False)
        self.txtPantalla.clear()


    # ===> Sexo <===
    def sexo(self):
        if self.rdbMasculino.isChecked():
            return 1
        else:
            return 0
    

    # ===> Tipo de beca <===
    def beca(self):
        if self.rdb100.isChecked():
            return 1
        elif self.rdb80.isChecked():
            return 2
        elif self.rdb50.isChecked():
            return 3
        else:
            return 0
    

    # ===>   Liista de materias   <===
    def materias(self):
        seleccion = ''
        materias = [
            self.ckbContabilidad,
            self.ckbEstadistica,
            self.ckbProgramacion,
            self.ckbBD,
            self.ckbOperaciones
        ]

        for materia in materias:
            if materia.isChecked():
                seleccion += (materia.text() + ', ')
        
        return seleccion[0:-2]

    # ===>   Tipo de beca | Para llenado de campos   <===
    def t_beca(self, tipo):
        if tipo == 1:
            beca = '100%'
        elif tipo == 2:
            beca = '80%'
        elif tipo == 3:
            beca = '50%'
        else:
            beca = 'Sin beca'
    
        return beca
    
    # ===>   Alumnos becados 100%   <===
    def becados(self):
        for registro in range(self.tbwTabla.rowCount()):
            if int(self.tbwTabla.item(registro, 10).text()) == 1:
                for celda in range(self.tbwTabla.columnCount()):
                    self.tbwTabla.item(registro, celda).setBackground(QtGui.QColor(87, 212, 158))
        
# ==> Inicio de la aplicación <==
app = QApplication(sys.argv)
UIWindows = UI()
UIWindows.show()
sys.exit(app.exec_())