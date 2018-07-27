# python

import lx
import lxu.command

class FunfCmdArg(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)
        self.dyna_Add('name', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(0, lx.symbol.fCMDARG_OPTIONAL)

    def basic_Execute(self, msg, flags):
        s = self.dyna_String(0, "no one")
        lx.out("Funf to " + s + "!")

lx.bless(FunfCmdArg, "funf.someone")

lx.out("I'm alive !!!")
