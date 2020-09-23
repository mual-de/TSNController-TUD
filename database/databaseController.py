import sqlite3
import xml.etree.ElementTree as ET
import logging

class DatabaseController():


    def __init__(self, pathToDatabase):
        self._conn_ = sqlite3.connect(pathToDatabase)
        logging.info("Database connection established")


    def addConfiguration(self, uuid, xmlConfig):
        logging.info("Added configuration to database")
        xmlStr = ET.tostring(xmlConfig, encoding='unicode')
        cmd = "INSERT INTO configurations VALUES (%s,%s)" %(uuid, xmlStr)
        c = self._conn_.cursor()
        c.execute(cmd)
        self._conn_.commit()

    def getAllConfigurationNames(self):
        c = self._conn_.cursor()
        c.execute("SELECT name FROM configurations")
        return c.fetchall()

    def getConfiguration(self, uuid):
        c = self._conn_.cursor()
        c.execute("SELECT config FROM configurations WHERE name=%s"%uuid)
        return ET.parse(c.fetchone())

    


