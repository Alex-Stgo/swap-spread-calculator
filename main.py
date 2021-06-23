import swaps as sw

curve = sw.curve(dir = r"curve.xls")
leg1 = sw.leg.VariableMXN(1000,13)
leg2 = sw.leg.FixedMXN(1000,12,0.04)
swap = sw.swap(leg1,leg2)
print(swap.spread())