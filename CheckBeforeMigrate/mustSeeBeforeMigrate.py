OntCversion = '2.0.0'
from ontology.interop.Ontology.Contract import Migrate
from ontology.interop.System.Storage import GetContext, Get, Put
from ontology.interop.System.Runtime import CheckWitness, GetTime, Notify
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash
from ontology.interop.Ontology.Native import Invoke
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.builtins import concat, state

from ontology.libont import AddressFromVmCode

"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/Utils.py
"""
def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)


"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeCheck.py
"""
def Require(condition):
    """
	If condition is not satisfied, return false
	:param condition: required condition
	:return: True or false
	"""
    if not condition:
        Revert()
    return True

def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    Require(len(key) == 20)
    return True

def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True


ONGAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')
ContractAddress = GetExecutingScriptHash()
Admin = Base58ToAddress("AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p")

TOTAL_ONG_KEY = "TotalONG"

def Main(operation, args):
    if operation == "deposit":
        if len(args) != 2:
            return False
        account = args[0]
        ongAmount = args[1]
        return deposit(account, ongAmount)

    if operation == "getTotalOng":
        return getTotalOng()
    if operation == "getDepositAmount":
        if len(args) != 1:
            return False
        account = args[0]
        return getDepositAmount(account)

    if operation == "migrateContract":
        if len(args) != 7:
            return False
        code = args[0]
        needStorage = args[1]
        name = args[2]
        version = args[3]
        author = args[4]
        email = args[5]
        description = args[6]
        return migrateContract(code, needStorage, name, version, author, email, description)
    return False



def deposit(account, ongAmount):
    RequireWitness(account)
    Require(_transferONG(account, ContractAddress, ongAmount))

    Put(GetContext(), concat("D_ONG", account), getDepositAmount(account) + ongAmount)
    Put(GetContext(), TOTAL_ONG_KEY, getTotalOng() + ongAmount)
    Notify(["deposit", account, ongAmount])
    return True

def getDepositAmount(account):
    return Get(GetContext(), concat("D_ONG", account))

def getTotalOng():
    return Get(GetContext(), TOTAL_ONG_KEY)

def migrateContract(code, needStorage, name, version, author, email, description):
    RequireWitness(Admin)
    # == Please Make sure transfer all the asset within the old contract to the new Contract
    # == If you do not transfer the assets including ONG, ONT, or OEP4 out,
    # == that means these assets will be out of your control for good.
    newReversedContractHash = AddressFromVmCode(code)
    res = _transferONGFromContact(newReversedContractHash, getTotalOng())
    Require(res)
    if res == True:
        res = Migrate(code, needStorage, name, version, author, email, description)
        Require(res)
        Notify(["Migrate Contract successfully", Admin, GetTime()])
        return True
    else:
        Notify(["MigrateContractError", "transfer ONG to new contract error"])
        return False


def _transferONG(fromAcct, toAcct, amount):
    """
    transfer ONG
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    RequireWitness(fromAcct)
    param = state(fromAcct, toAcct, amount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False

def _transferONGFromContact(toAcct, amount):
    param = state(ContractAddress, toAcct, amount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False