# Se recopilan en este documento las llamadas y las consultas a la bbdd para una mayor organización del código.

import psycopg2
from psycopg2.extras import RealDictCursor #para acceder al valor por el nombre de la columna

class BBDDMapHurricane:

    bbdd = None

    @staticmethod
    def instance():
        if BBDDMapHurricane.bbdd is None:
            BBDDMapHurricane.bbdd = BBDDMapHurricane()
        return BBDDMapHurricane.bbdd

    def __init__(self) -> None:
        self.con = psycopg2.connect("host='vmmaph' port='5432' dbname='maphurricane' user='maphurricane' password='Seresco_2000' connect_timeout=10 ")


    def ordenes_obtener(self): # Consulta para obtener las órdenes
        return self.ejecutar("SELECT o.t_id, codigo_orden, o.descripcion, e.descripcion estado FROM serladm.mh_orden_trabajo o left join serladm.tc_estadoorden e on o.estado_orden = e.t_id")


    def relordenpredio_obtenerpredios(self, idOrden: int) -> list[int]: # Consulta para obtener los predios
        rows = self.ejecutar(f"SELECT id_predio FROM serladm.rel_ordenpredio ro where id_ordentrabajo = {idOrden}")
        idsPredios = []
        for row in rows:
            idsPredios.append(row[0])
        return idsPredios
    
    def reluepredio_obtenerterrenos(self, idsPredios: list[int]) -> list[int]: # Consulta para obtener los terrenos
        idsPrediosConcat = ",".join(str(id) for id in idsPredios)
        rows = self.ejecutar(f"SELECT DISTINCT id_terreno from serladm.rel_uepredio where id_predio IN ({idsPrediosConcat}) and NOT id_terreno IS NULL")
        ids = []
        for row in rows:
            ids.append(row[0])
        return ids
    
    def reluepredio_obtenercontrucciones(self, idsPredios: list[int]) -> list[int]: # Consulta para obtener las construcciones
        idsPrediosConcat = ",".join(str(id) for id in idsPredios)
        rows = self.ejecutar(f"SELECT DISTINCT id_construccion from serladm.rel_uepredio where id_predio IN ({idsPrediosConcat}) and NOT id_construccion IS NULL")
        ids = []
        for row in rows:
            ids.append(row[0])
        return ids

    def reluepredio_obtenerunidadadescontruccion(self, idsPredios: list[int]) -> list[int]: # Consulta para obtener las unidades de construcción.
        idsPrediosConcat = ",".join(str(id) for id in idsPredios)
        rows = self.ejecutar(f"SELECT DISTINCT id_unidadconstruccion from serladm.rel_uepredio where id_predio IN ({idsPrediosConcat}) and NOT id_unidadconstruccion IS NULL")
        ids = []
        for row in rows:
            ids.append(row[0])
        return ids
    
    def rrrderecho_obteneridsinteresados(self, idsPredios: list[int]) -> list[int]: # Consulta para obtener los interesados.
        idsPrediosConcat = ",".join(str(id) for id in idsPredios)
        rows = self.ejecutar(f"SELECT DISTINCT id_interesado from serladm.rrr_derecho where id_predio IN ({idsPrediosConcat}) and NOT id_interesado IS NULL")
        ids = []
        for row in rows:
            ids.append(row[0])
        return ids

    def uapredio_buscarpornumeropredial(self, numero_predial): # Consulta para obtener los datos de los predios según el número predial
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT p.*, ru.id_terreno idt from serladm.ua_predio p left join serladm.rel_uepredio ru on ru.id_predio = p.t_id  WHERE numero_predial LIKE '%" + numero_predial + "%'")
        return cur.fetchone()

    def ueconstruccion_buscarporid (self, t_id): # Consulta para obtener las construcciones según su id
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"select uc.* from serladm.ue_construccion uc where t_id = {t_id}")
        return cur.fetchone()

    def intInteresados_BuscarPorId (self, t_id): # Consulta para obtener los interesados según su id
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"select ii.* from serladm.int_interesado ii where t_id = {t_id}")
        return cur.fetchone()
    
    def tc_obtenervalores(self, tabla): # Consulta para obtener las descripciones de campos relacionados en dos tablas
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute("""select t_id, descripcion from serladm.{} order by descripcion""".format(tabla))
        return cur.fetchall()

    def tc_obtenervaloresdireccion(self, tabla): # Consulta para obtener las descripciones de campos relacionados entre tres tablas
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"select e.t_id, td.descripcion from serladm.extdireccion e left join serladm.{tabla} td on td.t_id = e.tipo_direccion left join serladm.int_interesado ii on ii.id_direccion = e.t_id")
        return cur.fetchall()

    def ueUnidadconstruccion_BuscarIdUnidadconstruccion(self, id_construccion): # Consulta para obtener las unidades de construcción según su id
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute("""select distinct uu.t_id , uu.identificador from serladm.ue_unidadconstruccion uu where id_construccion = {} order by identificador""".format(id_construccion))
        return cur.fetchall()

    def agregar_contenido_construccion(self, id_predio): # Consulta para obtener los interesados según el id_predio
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute("""select distinct uc.t_id , uc.identificador from serladm.ue_construccion uc left join serladm.rel_uepredio ru on ru.id_construccion = uc.t_id where id_predio = {}""".format(id_predio))
        return cur.fetchall()

    def agregar_contenido_interesados(self, id_predio): # Consulta para obtener los interesados según el id_predio
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute("""select ii.t_id , ii.nombre, ii.documento_identidad from serladm.int_interesado ii left join serladm.rel_prediointeresado rp on rp.id_interesado = ii.t_id where id_predio = {}""".format(id_predio))
        return cur.fetchall()

    def uapredio_BuscarPorNumPredIdPreIdCon(self, numero_predial): # Consulta para obtener los predios según el número predial, el id_prediotipo y el id_condiciónpredio
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute("select up.t_id, numero_predial, tp.descripcion predio_tipo, tc.descripcion condicion_predio from serladm.ua_predio up left join serladm.tc_prediotipo tp on tp.t_id = up.id_prediotipo left join serladm.tc_condicionprediotipo tc on tc.t_id = up.id_condicionpredio where numero_predial like '%" + numero_predial + "%'")
        return cur.fetchall()

    def saca_numero_predial (self, x, y): # Consulta para obtener el número predial según las coordenadas x e y que se introduzcan.
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"select numero_predial from serladm.ue_terreno ut left join serladm.rel_uepredio ru on ru.id_terreno = ut.t_id left join serladm.ua_predio up on up.t_id = ru.id_predio where ST_Intersects(geometria, ST_SetSRID(st_point({(x)}, {(y)}),3857))")
        return cur.fetchone()['numero_predial']

    def ejecutar(self, sql):
        cur = self.con.cursor()
        cur.execute(sql)
        return cur.fetchall()