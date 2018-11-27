import matplotlib
matplotlib.use('Agg')
from qiskit import IBMQ, QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, Aer
from qiskit.qasm import pi
from qiskit.tools.visualization import (plot_histogram, 
                                        circuit_drawer, 
                                        matplotlib_circuit_drawer)
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import time
import datetime



IBMQ.load_accounts()
IBMQ.backends()


class QuantumWalk:

    def __init__(self, qubits, cbits):
        self.qubits = qubits
        self.cbits = cbits
        self.q = QuantumRegister(qubits)
        self.c = ClassicalRegister(cbits)
        self.qc = QuantumCircuit(self.q, self.c)

    def _QFT_dg(self):
        q = self.q
        qc = self.qc
        for n in range(1, self.qubits-1):
            qc.h(q[n])
            # print(n)
            for t in range(1, self.qubits-n):
                try:
                    qc.cu1(pi/(2**(t)), q[n], q[t+n])
                    # print(pi/(2**(t)), n, t+n)
                except:
                    continue
        qc.h(q[self.qubits-1])

    def _QFT(self):
        q = self.q
        qc = self.qc
        qc.h(q[self.qubits-1])
        for m in range(self.qubits-2, 0, -1):
            # print(m)
            for u in range(self.qubits, 0, -1):
                try:
                    qc.cu1(pi/(2**(u)), q[m+u], q[m])
                    # print(pi/(2**(u)), u+m, m)
                except:
                    continue
            qc.h(q[m])

    def _S_plus(self):
        q = self.q
        qc = self.qc
        coef = sum([1/2**i for i in range(2, self.qubits+1)])
        # print(coef)
        for i in range(1, self.qubits):
            qc.cx(q[i], q[0])
            qc.u1(-pi/2**(self.qubits-i), q[0])
            qc.cx(q[i], q[0])
        qc.u1(coef*pi, q[0])
        for j in range(self.qubits-1):
            # print(j)
            qc.u1(-pi/2**(self.qubits-j-1), q[j+1])

    def _S_minus(self):
        q = self.q
        qc = self.qc
        coef = sum([1/2**i for i in range(2, self.qubits+1)])
        # print([1/2**i for i in range(2, self.qubits+1)])
        # print(coef)
        for i in range(1, self.qubits):
            qc.cx(q[i], q[0])
            qc.u1(-pi/2**(self.qubits-i), q[0])
            qc.cx(q[i], q[0])
        qc.u1(coef*pi, q[0])
        for j in range(self.qubits-1):
            qc.u1(pi/2**(self.qubits-j-1), q[j+1])

    def walk(self):
        c = self.c
        q = self.q
        qc = self.qc

        qc.x(q[0])
        # qc.x(q[1])
        # qc.x(q[2])
        # initial coin operator
        self._coin_1()
        # step operator
        self._QFT_dg()
        self._S_plus()
        self._QFT()
        # initial coin operator2
        self._coin_2()
        # step operator
        self._QFT_dg()
        self._S_minus()
        self._QFT()
        # for i in range(1, self.qubits):
        #     qc.measure(q[i], c[i-1])
        for i in range(self.qubits):
            qc.barrier(q[i])
        for j in range(1, self.qubits):
            qc.measure(q[j], c[j-1])
        backends = ['ibmq_20_tokyo',
                    'qasm_simulator', 
                    'ibmqx_hpc_qasm_simulator']

        backend_sim = IBMQ.get_backend(backends[2])
        # backend_sim = Aer.get_backend(backends[1])

        result = execute(qc, backend_sim, shots=8192).result()
        # matplotlib_circuit_drawer(qc).show()

        m = result.get_counts(qc)
        keys = [int(k, 2) for k in m.keys()]
        values = [l/8192 for l in m.values()]

        # print(qc.qasm())
        # # circuit_drawer(qc).show()
        # plot_histogram(result.get_counts(qc))
        # plt.xlabel("position")
        # plt.ylabel("probability")
        # plt.bar(keys, values, width=0.8)
        # plt.show()
        # return keys, values
        return m

        # print(result.get_counts(qc))

    def _coin_1(self):

        c = self.c
        q = self.q
        qc = self.qc

        qc.cx(q[1], q[0])
        qc.u3(1/8, 0, 0, q[0])
        # qc.h(q[0])
        qc.cx(q[1], q[0])

    def _coin_2(self):
        c = self.c
        q = self.q
        qc = self.qc

        qc.cx(q[math.ceil(self.qubits/2)], q[0])
        qc.u3(1/8+pi/2, 0, 0, q[0])
        # qc.hq[0])
        qc.cx(q[math.ceil(self.qubits/2)], q[0])

    # def check(self):
    #     qc = self.qc
    #
    #     qc.h(q[0])
    #     qc.cx(q[0], q[1])
    #
    #     qc.measure(q, c)
    #     backends = ['ibmq_20_tokyo',
    #                 'qasm_simulator', 
    #                 'ibmqx_hpc_qasm_simulator']
    #
    #     backend_sim = IBMQ.get_backend(backends[0])
    #     # backend_sim = Aer.get_backend(backends[1])
    #
    #     result = execute(qc, backend_sim, shots=8192).result()
    #
    #
    #     m = result.get_counts(qc)
    #     keys = [int(k, 2) for k in m.keys()]
    #     values = [l/8192 for l in m.values()]
    #
    #     print(qc.qasm())
    #     circuit_drawer(qc).show()
    #     plot_histogram(result.get_counts(qc))
    #     plt.xlabel("position")
    #     plt.ylabel("probability")
    #     plt.bar(keys, values, width=0.8)
    #     plt.show()
    #
    #     print(result.get_counts(qc))
    
if __name__ == '__main__':
    results = []
    hel = []
    n = int(sys.argv[1])
    iteration = int(sys.argv[2])
    shots = 8192

    for i in range(iteration):
        start = time.time()
        print("this is now : %s" % str(i+1))
        a = QuantumWalk(n, n-1)
        results.append(a.walk())
        print("success")
        duration = time.time() - start
        print("Execution Time : %s" % str(duration))

    kln = [l for l in results[0].keys()]
    # kln = [bin(l).split("b")[1] for l in range(2**(n-1))]
    kln_int = [int(s, 2)-(2**(n-2))+1 for s in kln]

    for t in kln:
        vals = 0
        for s in results:
            try:
                vals += s[t]
            except:
                continue
        hel.append(vals/shots)
    fig = plt.figure()
    plt.xlabel("position")
    plt.ylabel("probability")
    plt.xlim([-2**(n), 2**(n)+1])
    plt.bar(kln_int, hel, width=0.8)
    #plt.show()
    tag = datetime.datetime.now()
    fig.savefig("./sim/%squbits/real_%stimes%s" % (str(n), str(iteration), (str(tag.month)+str(tag.day)+str(tag.hour)+str(tag.minute)+str(tag.second))))
    # fig.show()
    print("This is %s qubits quantum walk" % str(n))
