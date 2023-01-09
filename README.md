# electrotherm
Stepping Motors electro-thermal simulation schemes for LTSpice Simulator

Schemes:
* MotorControlHolding.asc - scheme simulates full bridge for phase of step motor in holding mode
	Dependent of subcircuit: HalfBridge.asc, Radiator.asc

* MotorControlStepping.asc - scheme simulates full bridge for phase of step motor in stepping mode
	Dependent of subcircuit: HalfBridge.asc, Radiator.asc

* MotorControlThermalOnly.asc - thermal only scheme for optimization of simulation 


Subcircuits:
* HalfBridge.asc - scheme of half bridge for current stabilization and control in step motor.
	Dependent of subcircuit: IRFB4615PBF_therm.asc, feedback.asc

* Radiator.asc - thermal scheme of heat sink Wakefield OMNI-UNI-30-50-D

* IRFB4615PBF_therm.asc - electro-thermal model of transistor IRFB4615PBF
	Dependent of subcircuit: irfb4615pbf.asy

* feedback.asc - logical block of current stabilization

* irfb4615pbf.asy - symbol for spice model irfb4615pbf.spi

Quickstart:
 - Download Infineon spice-model file of transistor irfb4615pbf.spi. 
 Link: https://www.infineon.com/dgdl/irfb4615pbf.spi?fileId=5546d462533600a4015357128143396c
 - Change next parameters for .MODEL MM:
.MODEL MM NMOS LEVEL=3 IS=1e-32
+VTO=Vth NFS=1.988288E+12 KP=74.89621574661534 THETA=0.31480607500134106 KAPPA=42.67943561393658 VMAX = 4E+3
+NSUB=1E+15 PHI=0.576 GAMMA=0.5276 TOX=1E-07 XJ = 0 DELTA=0
 - Change RS:
RS 8 3 0.0001
 - Change RD:
RD 9 1 {Rds_val}
 - Open asc-file in LTSpice and press Run button

Optimization of simulation
Running of scheme such as MotorControlHolding.asc for long period of simulation may take of very long time.
So it needs to use optimization: first to run MotorControlHolding.asc for short period (a few millisecond),
take powers of transistors and put to simple thermal-only circuit, next take temperatures of transistors
and put to full scheme and so on.
This algorithm is realized in Python-program in directory run. To use it:
 - Configure default.ini file
 - Run run.py
 - At the end of simulation results will be in console and all raw-files
