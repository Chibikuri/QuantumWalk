# -*- coding: utf-8 -*-
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import time
import datetime
from qiskit import IBMQ, QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, Aer
from qiskit.qasm import pi
from qiskit.tools.visualization import plot_histogram, circuit_drawer, matplotlib_circuit_drawer
# matplotlib.use('Agg')
IBMQ.load_accounts()
IBMQ.backends()


class QuantumWalk:

    def __init__(self, qubits, cbits):
        self.qubits = qubits
        self.cbits = cbits
        self.q = QuantumRegister(qubits)
        self.c = ClassicalRegister(cbits)
        self.qc = QuantumCircuit(self.q, self.c)

    def _QFT_dg(self, circuit):
        q = self.q
        qc = circuit
        for n in range(1, self.qubits):
            # print(n)
            qc.h(q[n])
            for t in range(1, self.qubits-n):
                try:
                    qc.cu1(pi/(2**(t)), q[n], q[n+t])
                    # print(pi/(2**(t)), n, t+n)
                except:
                    continue

    def _QFT(self, circuit):
        q = self.q
        qc = circuit
        for m in range(self.qubits-1, 0, -1):
            for u in range(self.qubits, 0, -1):
                try:
                    qc.cu1(-pi/(2**(u)), q[m+u], q[m])
                except:
                    continue
            qc.h(q[m])

    def _S_plus(self, circuit):
        q = self.q
        qc = circuit
        coef = sum([1/2**i for i in range(1, self.qubits)])
        for i in range(1, self.qubits):
            qc.cx(q[i], q[0])
            qc.u1(pi/2**(self.qubits-i), q[0])
            qc.cx(q[i], q[0])
        qc.u1(-coef*pi, q[0])
        for j in range(self.qubits-1):
            qc.u1(pi/2**(self.qubits-j-1), q[j+1])

    def _S_minus(self, circuit):
        q = self.q
        qc = circuit
        coef = sum([1/(2**i) for i in range(1, self.qubits)])
        for i in range(1, self.qubits):
            qc.cx(q[i], q[0])
            qc.u1(pi/2**(self.qubits-i), q[0])
            qc.cx(q[i], q[0])
        qc.u1(-coef*pi, q[0])
        for j in range(self.qubits-1):
            qc.u1(-pi/2**(self.qubits-j-1), q[j+1])

    def walk(self, step):
        c = self.c
        q = self.q
        qc = self.qc

        # qc.x(q[1])
        qc.x(q[self.qubits-1])
        # initial coin perator
        for i in range(step):
            self._coin_1(-0.4, -0.4, qc)
            # self.check_qft_dg()
            self._QFT_dg(qc)
            self._S_plus(qc)
            self._QFT(qc)
        for j in range(step):
            # initial coin operator2
            self._coin_2(-0.4-pi, 0.4+pi, qc)
            self._QFT_dg(qc)
            self._S_minus(qc)
            self._QFT(qc)

        for i in range(self.qubits):
            qc.barrier(q[i])

        mq = [j for j in range(self.qubits-1, 0, -1)]
        mc = [k for k in range(self.qubits-1)]
        for j, k in zip(mq, mc):
            qc.measure(q[j], c[k])

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
        # plot_histogram(result.get_counts(qc))
        # print(qc.qasm())
        return m

    def _coin_1(self, theta1p, theta1m, circuit):
        q = self.q
        qc = circuit

        qc.u3(-(theta1p+theta1m)/2, 0, 0, q[0])
        qc.cx(q[1], q[0])
        qc.u3(-(theta1p-theta1m)/2, 0, 0, q[0])
        qc.cx(q[1], q[0])

    def _coin_2(self, theta2p, theta2m, circuit):
        q = self.q
        qc = circuit

        qc.u3(-(theta2p+theta2m)/2, 0, 0, q[0])
        qc.cx(q[1], q[0])
        qc.u3(-(theta2p-theta2m)/2, 0, 0, q[0])
        qc.cx(q[1], q[0])


if __name__ == '__main__':
    results = []
    hel = []
    n = int(sys.argv[1])
    steps = int(sys.argv[2])
    shots = 8192

    # for i in range(steps):
    start = time.time()
    print("this is now : %s" % str(steps), "steps")
    a = QuantumWalk(n, n)
    m = a.walk(steps)
    results.append(m)
    print(m)
    print("success")
    duration = time.time() - start
    print("Execution Time : %s" % str(duration))

    kln = [format(l, '0%sb' % (str(n))) for l in range(2**(n))]
    kln_int = [int(s, 2) for s in kln]
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
    plt.xlim([-2**(n-1), 2**(n-1)+1])
    plt.ylim([0, 1.0])
    plt.bar(kln_int, hel, width=0.8)
    tag = datetime.datetime.now()
    fig.savefig("./sim/%squbits/%ssteps%s" % (str(n), str(steps), (str(tag.month)+str(tag.day)+str(tag.hour)+str(tag.minute)+str(tag.second))))
    print("This is %s qubits quantum walk" % str(n))
