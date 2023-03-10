

from pyteal import *
from beaker import *


class FundIN(Application):

  name = ApplicationStateValue(stack_type=TealType.bytes, default=Bytes(""))
  imageURL = ApplicationStateValue(stack_type=TealType.bytes, default=Bytes(""))
  description = ApplicationStateValue(stack_type=TealType.bytes, default=Bytes(""))
  date = ApplicationStateValue(stack_type=TealType.uint64, default=Int(0))
  amountNeeded = ApplicationStateValue(stack_type=TealType.uint64, default=Int(0))
  amountRaised = ApplicationStateValue(stack_type=TealType.uint64, default=Int(0))

  can_donate = ApplicationStateValue(stack_type=TealType.uint64, default=Int(1))

  FEE = Int(1000)

  @create
  def create(
    self,
    name: abi.String,
    imageURL: abi.String,
    description: abi.String,
    amountNeeded: abi.Uint64, 

  ):
    return Seq(
      
      Assert(name.get() != Bytes("")),
      Assert(imageURL.get() != Bytes("")),
      Assert(description.get() != Bytes("")),
      Assert(amountNeeded.get() > Int(0)),
      Assert(Txn.note() == Bytes("FundINFUndIN: uv1")),

      self.name.set(name.get()),
      self.imageURL.set(imageURL.get()),
      self.description.set(description.get()),
      self.date.set(self.date.get() + Global.latest_timestamp()),
      self.amountNeeded.set(amountNeeded.get()),

    )

  @external
  def donate(
    self,
    paymentTxn: abi.PaymentTransaction
  ):
    return Seq(
      Assert(self.can_donate == Int(1)),

      Assert(self.amountNeeded < self.amountRaised),
      Assert(paymentTxn.get().amount() > Int(0)),
      Assert(paymentTxn.get().receiver() == self.address),

      self.amountRaised.set(self.amountRaised.get() + paymentTxn.get().amount()),

      
    )

  @external
  def transferToCreator(self):
    return Seq(
      Assert(
        And(
          self.amountRaised >= self.amountNeeded
        )
      ),

      InnerTxnBuilder.Execute({
        TxnField.type_enum(): TxnType.Payment,
        TxnField.receiver(): Global.creator_address(),
        TxnField.amount(): self.amountRaised,
        TxnField.fee: self.FEE


      }),
      # set can_donate to 0
      self.can_donate.set(Int(0))
    )

  @external(authorize=Authorize.only(Global.creator_address()))
  def editApplication(
    self,
    name: abi.String,
    imageURL: abi.String,
    description: abi.String,
    amountNeeded: abi.Uint64,
    amountRaised: abi.Uint64, 

  ):
    return Seq(
      Assert(self.can_donate == Int(1)),

      self.name.set(name.get()),
      self.imageURL.set(imageURL.get()),
      self.description.set(description.get()),
      self.amountNeeded.set(amountNeeded.get()),
      self.amountRaised.set(amountRaised.get())
    )

FundIN().dump("./artifacts")