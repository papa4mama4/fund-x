
from pyteal import *

from fundx import Funding

if __name__ == "__main__":
    approval_program = Funding().approval_program()
    clear_program = Funding().clear_program()

    # Mode.Application specifies that this is a smart contract
    compiled_approval = compileTeal(approval_program, Mode.Application, version=6)
    print(compiled_approval)
    with open("funding_approval.teal", "w") as teal:
        teal.write(compiled_approval)
        teal.close()

    # Mode.Application specifies that this is a smart contract
    compiled_clear = compileTeal(clear_program, Mode.Application, version=6)
    print(compiled_clear)
    with open("funding_clear.teal", "w") as teal:
        teal.write(compiled_clear)
        teal.close()
