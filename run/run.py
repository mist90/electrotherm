#!/usr/bin/env python3


#    MIT License
#  Copyright (c) 2022 Mikhail Tegin
#  michail3110@gmail.com
#  
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import sys
import os
import signal
import configparser
import json
import re
import numpy as np

def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def StopCriteriaVector(names, varsDict):
    return np.array([float(varsDict.get(n)) for n in names])

# Substitute value of varName to varValue in scheme fileName
def SubstituteValue(fileName, varName, varValue):
    file = open(fileName, 'r', encoding = 'iso8859_15')
    text = file.read()
    text = re.sub(r'(.*\.param {})=[0-9.+-e]*'.format(varName), r'\1={}'.format(varValue), text)
    with open(fileName, 'w', encoding='iso8859_15') as file:
        file.write(text)

# Get value of varName from scheme fileName
def GetValue(fileName, varName):
    file = open(fileName, 'r', encoding = 'utf_16_le')
    text = file.read()
    m = re.search(r'{}: .*=([0-9.+-e]*) (FROM|at).*'.format(varName), text)
    if m == None:
        return None
    return m.group(1)

def Exec(execFile, ascfile):
    proc = os.popen(execFile + " -Run -b {}".format(ascfile))
    print(proc.read())

stop = 0
def SigintHandler(one, two):
    global stop
    stop = 1
    print("Stopped")

# Getting config name from command line
if len(sys.argv) > 1:
    configName = sys.argv[1]
else:
    configName = "default.ini"

print('Open config file:' + configName)

# Reading configuration file
cfg = configparser.ConfigParser()
cfg.read(configName)

exefile = cfg.get('Parameters', 'LTSPICE_EXE')
ascfile1 = cfg.get('Parameters', 'asc1')
ascfile2 = cfg.get('Parameters', 'asc2')
logfile1 = cfg.get('Parameters', 'log1')
logfile2 = cfg.get('Parameters', 'log2')
nIter = int(cfg.get('Parameters', 'nIter'))

variables1 = dict(cfg.items("Variables1"))
variables2 = dict(cfg.items("Variables2"))

maxValueStopCriteria = float(cfg.get('StopCriteria', 'Maximum'))
varNameStopCriteria = json.loads(cfg.get('StopCriteria', 'Vector'))

signal.signal(signal.SIGINT, SigintHandler)

for iter in range(nIter):
    print("**** Iteration: {} ****".format(iter + 1))
    if stop:
        break
    
    # Updating variables1 in the scheme ascfile1
    for name,value in variables1.items():
        if IsNumber(value):
            SubstituteValue(ascfile1, name, value)

    # Running LTSpice for scheme ascfile1
    Exec(exefile, ascfile1)
    
    # Reading results from ascfile1 and copying them in dictionary variables2 for scheme ascfile2
    for name,value in variables2.items():
        val = GetValue(logfile1, name)
        if val != None:
            variables2[name] = val
    
    # Updating variables2 in the scheme ascfile2
    for name,value in variables2.items():
        if IsNumber(value):
            SubstituteValue(ascfile2, name, value)
    
    # Print variables for scheme ascfile2
    print("Scheme 2 variables:")
    for name,value in variables2.items():
        print("{}: {}".format(name, value))
    
    if stop:
        break
    
    # Running LTSpice for scheme ascfile2
    Exec(exefile, ascfile2)
    
    # Reading results from ascfile2 and copying them in dictionary variables1 for scheme ascfile1
    for name,value in variables1.items():
        val = GetValue(logfile2, name)
        if val != None:
            variables1[name] = val
    
    # Print variables for scheme ascfile1
    print("Scheme 1 variables:")
    for name,value in variables1.items():
        print("{}: {}".format(name, value))
    
    if iter == 0:
        prevVector = StopCriteriaVector(varNameStopCriteria, variables1 | variables2)
    else:
        vector = StopCriteriaVector(varNameStopCriteria, variables1 | variables2)
        norm = np.linalg.norm(vector - prevVector)
        print("Current norm value: ", norm)
        prevVector = vector
        if norm < maxValueStopCriteria:
            break
print("Finished")
