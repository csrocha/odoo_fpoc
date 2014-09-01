
# Fiscal Printer for OpenERP

Este módulo está desarrollado por el grupo de la localización Argentina de OpenERP y
tiene como objetivo la administración y uso de impresoras fiscales para la 
impresión de tickets.

# Aplicativo Chome para Impresoras Fiscales

El módulo requiere que los clientes que tengan conectado las impresoras fiscales
tengan corriendo/ejecutando el Aplicativo Chrome para Impresoras Fiscales. El mismo
lo pueden conseguir en:

https://github.com/csrocha/fp-chrome-app-oerp

# Impresoras Homologadas por la AFIP

Para conocer que impresoras están soportadas en el módulo, hay que revisar la lista
en el Aplicativo Chrome de Impresoras Fiscales para OpenERP. 

# Instalación

Se tiene que hacer disponible los siguientes módulos:

    addons/fiscal_printer
    addons/x_fiscal_printer

Con solo instalar x_fiscal_priter es suficiente.

# Desarrollando para este módulo

El módulo tiene una punta para el diseño y otro para el desarrollo.

Para el diseño hay que utilizar la herramienta ArgoUML (http://argouml.tigris.org/)
y utilizar XMI2OERP (https://github.com/csrocha/xmi2oerp) para generar el código.
El archivo XMI del diseño se encuentra en el directorio design. He dejado un Makefile
para que con un simple "make" luego de retocar el UML se pueda generar el código.

Si se necesita programar hay que realizarlo en el módulo addons/x_fiscal_printer.
Esto es porque cada vez que se genera el código desde el UML se pierde cualquier
cambio que exista en el directorio destino que es addons/fiscal_printer.

