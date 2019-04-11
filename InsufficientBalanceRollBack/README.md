Suppose the player who is betting bet all his account balance, then if the player wins he will receive double amount of his betting ONG amount.

Yet, if the player loses, then since he cannot pay for the invoking/executing fee of ```bet``` function because he has transferred all his balance amount of ONG to the contract, the transaction will roll back.

So, if the player keeps betting all the balance in every round, he can make sure he always wins since otherwise the transaction will fail.

Here, we provide a solution which is:
```angular2html
#======================= avoid to be attacked begin ================
minAmount = ongAmount + MinInvokeFee
Require(_avoidInsufficientBalanceRollBackAttack(account, minAmount))
# ======================= avoid to be attacked end =================
```
Here is the explanation.

We need to check his balance is sufficient before his betting is effective to make sure his balance is enough to pay for the transaction fee.
Otherwise, the contract will directly reject his betting.