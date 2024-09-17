from sys import argv
from Client_Ops import Client_Ops
import USBHub.QAPaths as QAPaths

to_uninstall = []
package_name = QAPaths.client_packageName

Client_Ops().install_to_all(argv[1])
