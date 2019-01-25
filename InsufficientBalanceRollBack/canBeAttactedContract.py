OntCversion = '2.0.0'
from ontology.interop.Ontology.Contract import Migrate
from ontology.interop.System.App import RegisterAppCall, DynamicAppCall
from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import CheckWitness, GetTime, Notify, Serialize, Deserialize
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash, GetScriptContainer
from ontology.interop.Ontology.Native import Invoke
from ontology.interop.Ontology.Runtime import GetCurrentBlockHash, Base58ToAddress
from ontology.builtins import concat, state, sha256
from ontology.interop.System.Transaction import GetTransactionHash
from ontology.libont import int, elt_in, str
from ontology.builtins import abs

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
# 0.1 ONG
MinInvokeFee = 100000000


def Main(operation, args):
    if operation == "bet":
        if len(args) != 3:
            return False
        account = args[0]
        ongAmount = args[1]
        number = args[2]
        return bet(account, ongAmount, number)

    return False

def bet(account, ongAmount, number):
    """
    :param account:
    :param ongAmount:
    :param number: the range is between 1 to 100, [1, 100]
    :return:
    """
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # bet: Check witness failed!
        return False

    # #======================= avoid to be attacked begin ================
    # minAmount = ongAmount + MinInvokeFee
    # Require(_avoidInsufficientBalanceRollBackAttack(account, minAmount))
    # # ======================= avoid to be attacked end =================

    Require(_transferONG(account, ContractAddress, ongAmount))
    randomNumber = _rollANumber()
    if number < randomNumber:
        # the account will win, contract will pay a certain amount of ONG to the player
        # suppose the odds is 2
        Require(_transferONGFromContact(account, 2*ongAmount))
    # if number >= randomNumber the account/player will lose all his money
    return True



def _avoidInsufficientBalanceRollBackAttack(account, minAmount):
    param = state(account)
    # do not use [param]
    ongBalance = Invoke(0, ONGAddress, 'balanceOf', param)
    Require(ongBalance > minAmount)
    return True

def _rollANumber():
    blockHash = GetCurrentBlockHash()
    tx = GetScriptContainer()
    txhash = GetTransactionHash(tx)
    theNumber = abs(blockHash ^ txhash) % 100
    theNumber = abs(theNumber) + 1
    return theNumber

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