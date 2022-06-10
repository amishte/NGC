import pyvisa

rm = pyvisa.ResourceManager()
inst = rm.open_resource("ASRL3::INSTR")
print(inst.query("*IDN?"))

inst.write("FREQ 1000")

inst.write("APHS")

print("Phase Value: ")
print(inst.query("PHAS?"))

x = inst.query("OUTP? 1")
y = inst.query("OUTP? 2")
r = inst.query("OUTP? 3")
theta = inst.query("OUTP? 4")

c = float(x)/(2*3.1415*1000*.004)*10**12

print(f"Output Values:\n X {x} Y {y} R {r} Theta {theta}")

print(f"Cap?: {c}")


