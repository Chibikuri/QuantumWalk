from qiskit import IBMQ, QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, Aer
from qiskit.qasm import pi
from qiskit.tools.visualization import plot_histogram, circuit_drawer, matplotlib_circuit_drawer
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import time
from datetime import datetime

IBMQ.load_accounts()
IBMQ.backends()

def monitor():
    q = QuantumRegister(1)
    c = ClassicalRegister(1)
    qc = QuantumCircuit(q, c)
    qc.x(q[0])
    qc.measure(q, c)

    backend_sim = IBMQ.get_backend('ibmqx_hpc_qasm_simulator')
    result = execute(qc, backend_sim, shots=100).result()


if __name__ == '__main__':
    times = []
    durations = []
    iteration = 10
    for i in range(iteration):
        start = time.time()
        print("this is now : %s" % str(i+1))
        monitor()
        print("success")
        times.append(datetime.now())
        duration = time.time() - start
        if i % 50 == 0:
            durations.append(duration)
        print("Execution Time : %s" % str(duration))
        # time.sleep(5)

    plt.xlabel("time")
    plt.ylabel("response time")
    plt.plot(times, durations)
    plt.show()
