
from pyteal import *


class Funding:
	class Variables:
		name = Bytes("NAME")
		description = Bytes("DESCRIPTION")
		amountNeeded = Bytes("AMOUNTNEEDED")


		amountRaised = Bytes("AMOUNTRAISED")
		date = Bytes("DATE")
		can_donate = Bytes("CAN_DONATE")


	class AppMethods:
		donate = Bytes("donate")
		transferToCreator = Bytes("transferToCreator")
	
	def application_creation(self):
		return Seq([
			Assert(Txn.application_args.length() == Int(3)),
			Assert(Txn.note() == Bytes("FundINFUndIN: uv1")),
			Assert(Btoi(Txn.application_args[2]) > Int(0)),
			App.globalPut(self.Variables.name, Txn.application_args[0]),
			App.globalPut(self.Variables.description, Txn.application_args[1]),
			App.globalPut(self.Variables.amountNeeded, Btoi(Txn.application_args[2])),

			App.globalPut(self.Variables.amountRaised, Int(0)),
			App.globalPut(self.Variables.can_donate, Int(1)),
			App.globalPut(self.Variables.date, Global.latest_timestamp()),
			Approve()
		])

	def donate(self):
		return Seq([
			Assert(
				And(
					Global.group_size() == Int(2),

					Gtxn[1].type_enum() == TxnType.Payment,
					Gtxn[1].receiver() == Global.creator_address(),
					Gtxn[1].amount() > Int(1000),
					Gtxn[1].sender() == Gtxn[0].sender(),

					App.globalGet(self.Variables.can_donate) == Int(1),
					App.globalGet(self.Variables.amountNeeded) >= App.globalGet(self.Variables.amountRaised)					

				)
			),

			App.globalPut(self.Variables.amountRaised, App.globalGet(self.Variables.amountRaised) + Gtxn[1].amount()),
			Approve()
		])


	def transferToCreator(self):
		return Seq([
			Assert(
				App.globalGet(self.Variables.amountRaised) >= App.globalGet(self.Variables.amountNeeded)
			),

			InnerTxnBuilder.Begin(),
			InnerTxnBuilder.SetFields(
				{

					TxnField.type_enum: TxnType.Payment,
					TxnField.receiver: Global.creator_address(),
					TxnField.amount: App.globalGet(self.Variables.amountRaised),
					TxnField.fee: Int(1000)

				}
			),
			InnerTxnBuilder.Submit(),
			# set can_donate to 0
			App.globalPut(self.Variables.can_donate, Int(0)),
			Approve()
		])


	def application_deletion(self):
		return Return(Txn.sender() == Global.creator_address())

	def application_start(self):
		return Cond(
			[Txn.application_id() == Int(0), self.application_creation()],
			[Txn.on_completion() == OnComplete.DeleteApplication, self.application_deletion()],
			[Txn.application_args[0] == self.AppMethods.donate, self.donate()],
			[Txn.application_args[0] == self.AppMethods.transferToCreator, self.transferToCreator()]
    )

	def approval_program(self):
		return self.application_start()

	def clear_program(self):
		return Return(Int(1))