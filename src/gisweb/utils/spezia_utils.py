# - coding: utf-8 -

from lxml import etree
import xmlrpclib
from datetime import datetime
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def initBody4spezia():

#    page = etree.Element('xml', version='1.0', encoding='ISO-8859-1')
    
    segnatura_info = {'{http://www.w3.org/XML/1998/namespace}lang': 'it'}
    segnatura = etree.Element('Segnatura', **segnatura_info)
    
    doc = etree.ElementTree(segnatura)
    
#    segnatura_info = {'{http://www.w3.org/XML/1998/namespace}lang': 'it'}
#    segnatura = etree.SubElement(page, 'Segnatura', **segnatura_info)
    
    intestazione = etree.SubElement(segnatura, 'Intestazione')

    identificatore = etree.SubElement(intestazione, 'Identificatore')

    parent = etree.SubElement(identificatore, 'CodiceAmministrazione')
    id_aoo = etree.SubElement(identificatore, 'CodiceAOO')
    idRichiesta = etree.SubElement(identificatore, 'NumeroRegistrazione')
    data_segnatura = etree.SubElement(identificatore, 'DataRegistrazione')
    
    origine = etree.SubElement(intestazione, 'Origine')

    indirizzotelematico = etree.SubElement(origine, 'IndirizzoTelematico')
    mittente = etree.SubElement(origine, 'Mittente')

    amministrazione = etree.SubElement(mittente, 'Amministrazione')
    nominativo = etree.SubElement(amministrazione, 'Denominazione')
    unitaorganizzativa = etree.SubElement(amministrazione, 'UnitaOrganizzativa')
    denominazione = etree.SubElement(unitaorganizzativa, 'Denominazione')
    indirizzopostale = etree.SubElement(unitaorganizzativa, 'IndirizzoPostale')
    indirizzo = etree.SubElement(indirizzopostale, 'Toponimo')
    civico = etree.SubElement(indirizzopostale, 'Civico')
    cap = etree.SubElement(indirizzopostale, 'CAP')
    comune = etree.SubElement(indirizzopostale, 'Comune')
    provincia = etree.SubElement(indirizzopostale, 'Provincia')
    
    aoo = etree.SubElement(mittente, 'AOO')
    denominazione = etree.SubElement(aoo, 'Denominazione')
    
    destinazione = etree.SubElement(intestazione, 'Destinazione', confermaRicezione='si')
    IndirizzoTelematico = etree.SubElement(destinazione, 'IndirizzoTelematico', tipo='uri')
    
    risposta = etree.SubElement(intestazione, 'Risposta')
    responseURL = etree.SubElement(risposta, 'IndirizzoTelematico')
    
    riservato = etree.SubElement(intestazione, 'Riservato')
    riservato.text = 'N'
    
    oggetto = etree.SubElement(intestazione, 'Oggetto')
    note = etree.SubElement(intestazione, 'Note')
    
    riferimenti = etree.SubElement(segnatura, 'Riferimenti')
    
    contestoprocedurale = etree.SubElement(riferimenti, 'ContestoProcedurale')
    
    utenteProtocollatore  = etree.SubElement(contestoprocedurale, 'CodiceAmministrazione')
    cp_aoo = etree.SubElement(contestoprocedurale, 'CodiceAOO')
    identificativo = etree.SubElement(contestoprocedurale, 'Identificativo')
    tipocontesto = etree.SubElement(contestoprocedurale, 'TipoContestoProcedurale')
    classifica0 = etree.SubElement(contestoprocedurale, 'Classifica')

    titolario = etree.SubElement(classifica0, 'Livello')
    classifica = etree.SubElement(classifica0, 'Livello')
    cl_l3 = etree.SubElement(classifica0, 'Livello')
    cl_l3.text = '0'
    
    descrizione = etree.SubElement(segnatura, 'Descrizione')
    documento = etree.SubElement(descrizione, 'Documento', tipoRiferimento='MIME')
    
    return locals()

def getXmlBody(
        parent = '86',
        titolario = '6',
        classifica = '7',
        tipocontesto = 'IndicazioneClassificazione',
        utenteProtocollatore = 'dammau54',
        responseURL = "http://protocollo.spezia.vmserver/ws_protocollo.php", # URL di test
        **kwdata):

    data = locals()
    kwdata = data.pop('kwdata')
    data.update(kwdata)

    bodyParts = initBody4spezia()

    for k,v in data.items():
        if k in bodyParts:
            bodyParts[k].text = v
    
    xmlfile = StringIO()
    bodyParts['doc'].write(xmlfile)
    body = xmlfile.getvalue()
    xmlfile.close()

    return body

service_url = 'http://protocollo.spezia.vmserver/ws_protocollo.php'
def protocolla(served_url, kwargs, test=1):
    
    now = datetime.now()
    data = now.strftime('%Y-%m-%d %H:%M:%S')
    xml_content = getXmlBody(**kwargs)
    if test:
        num = now.strftime('%s')
    server = xmlrpclib.Server(service_url)
    response = server.accoda(data, num, served_url, xml_content.encode('base64'))
    return response.decode('base64')

if __name__ == '__main__':
    kwargs ={'oggetto':u'test', 'nominativo':u'manuele pesenti',
        'indirizzo':u'via A. Gramsci', 'cap':u'16100','comune':u'Genova',
        'provincia':u'GE', 'username':u'pippo', 'tipo':u'scavi'}
    served_url = "http://iol.vmserver/scavicantieri/application/test"
    server = xmlrpclib.Server(service_url)
#    print server.system.listMethods()
#    print getXmlBody(**kwargs)
    
    print protocolla(served_url, kwargs)
    
