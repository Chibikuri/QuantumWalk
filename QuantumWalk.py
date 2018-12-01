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

    def _QFT(self):
        q = self.q
        qc = self.qc
        qc.h(q[self.qubits-1])
        for n in range(1, self.qubits-1):
            # print(n)
            for t in range(1, self.qubits-n):
                try:
                    qc.cu1(-pi/(2**(t)), q[t], q[t+n])
                    # print(pi/(2**(t)), n, t+n)
                except:
                    continue
            qc.h(q[n])
        

    def _QFT_dg(self):
        q = self.q
        qc = self.qc
        
        for m in range(self.qubits-2, 0, -1):
            # print(m)
            qc.h(q[m])
            for u in range(self.qubits, 0, -1):
                try:
                    qc.cu1(pi/(2**(u)), q[m+u], q[m])
                    #print(pi/(2**(u)), m+u, m)
                except:
                    #print("error")
                    continue
        qc.h(q[self.qubits-1])
            

    # def check_qft_dg(self):
    #     q = self.q
    #     qc = self.qc 
    #     qc.h(q[1])
    #     qc.u1(pi/4, q[1]) 
    #     qc.u1(pi/4, q[2])
    #     qc.cx(q[1], q[2])
    #     qc.u1(-pi/4, q[2]) 
    #     qc.cx(q[1], q[2])
    #     qc.h(q[2])

    # def check_qft(self):
    #     q = self.q
    #     qc = self.qc 
    #     qc.h(q[2])
    #     qc.cx(q[1], q[2])
    #     qc.u1(pi/4, q[2]) 
    #     qc.cx(q[1], q[2])
    #     qc.u1(-pi/4, q[1]) 
    #     qc.u1(-pi/4, q[2])

    #     qc.h(q[1])

        
    # def qft(self, circ, q, n):
    #     """n-qubit QFT on q in circ."""
    #     circ.h(q[2])
    #     for j in range(1, n):
    #         for k in range(1, j):
    #             circ.cu1(math.pi/float(2**(j-k)), q[j], q[k])
    #         # circ.h(q[j])
    #     circ.h(q[1])

    def _S_plus(self):
        q = self.q
        qc = self.qc
        coef = sum([1/2**i for i in range(1, self.qubits)])
        for i in range(1, self.qubits):
            qc.cx(q[i], q[0])
            qc.u1(pi/2**(self.qubits-i), q[0])
            qc.cx(q[i], q[0])
        qc.u1(-coef*pi, q[0])
        for j in range(self.qubits-1):
            qc.u1(pi/2**(self.qubits-j-1), q[j+1])

    def _S_minus(self):
        q = self.q
        qc = self.qc
        coef = sum([1/(2**i) for i in range(1, self.qubits)])
        for i in range(1, self.qubits):
            qc.cx(q[i], q[0])
            qc.u1(pi/2**(self.qubits-i), q[0])
            qc.cx(q[i], q[0])
        qc.u1(-coef*pi, q[0])
        for j in range(self.qubits-1):
            qc.u1(-pi/2**(self.qubits-j-1), q[j+1])
        print([1/(2**i) for i in range(2, self.qubits+1)])

    def walk(self):
        c = self.c
        q = self.q
        qc = self.qc

        qc.x(q[self.qubits - 1])
        # initial coin operator
        self._coin_1()
        # self.check_qft_dg()
        self._QFT_dg()
        self._S_plus()
        self._QFT()

        # initial coin operator2
        self._coin_2()
        self._QFT_dg()
        self._S_minus()
        self._QFT()

        for i in range(self.qubits):
            qc.barrier(q[i])
        
        mq = [j for j in range(self.qubits-1, 0, -1)]
        mc = [k for k in range(self.qubits-1)]
        for j, k in zip(mq, mc):
           qc.measure(q[j], c[k])
        # qc.measure(q[1], c[1])
        # qc.measure(q[2], c[0])
        # qc.measure(q, c)
        backends = ['ibmq_20_tokyo',
                    'qasm_simulator', 
                    'ibmqx_hpc_qasm_simulator']

        backend_sim = IBMQ.get_backend(backends[0])
        # backend_sim = Aer.get_backend(backends[1])

        result = execute(qc, backend_sim, shots=8192).result()
        matplotlib_circuit_drawer(qc).show()

        m = result.get_counts(qc)
        keys = [int(k, 2) for k in m.keys()]
        values = [l/8192 for l in m.values()]

        # print(qc.qasm())
        return m 

    def _coin_1(self):

        c = self.c
        q = self.q
        qc = self.qc

        # qc.cx(q[1], q[0])
        qc.u3(0.4, 0, 0, q[0])
        # qc.cx(q[1], q[0])

    def _coin_2(self):
        c = self.c
        q = self.q
        qc = self.qc

        qc.cx(q[1], q[0])
        qc.u3(0.4+pi, 0, 0, q[0])
        qc.cx(q[1], q[0])

    
if __name__ == '__main__':
    results = []
    hel = []
    n = int(sys.argv[1])
    iteration = int(sys.argv[2])
    shots = 8192

    for i in range(iteration):
        start = time.time()
        print("this is now : %s" % str(i+1))
        a = QuantumWalk(n, n)
        m = a.walk()
        results.append(m)
        print(m)
        print("success")
        duration = time.time() - start
        print("Execution Time : %s" % str(duration))

    
        # plot_histogram(a)
    # print(results)

    kln = [format(l, '0%sb' % (str(n))) for l in range(2**(n))]
    # kln = [bin(l).split("b")[1] for l in range(2**(n-1))]
    kln_int = [int(s, 2) for s in kln]
    # print(kln)
    # print(results)
    # print(kln_int)
    for t in kln:
        vals = 0
        for s in results:
            try:
                vals += s[t]
                # print(vals)
            except:
                #print("keyerror", t)
                continue
        # print(vals/shots*iteration)
        hel.append(vals/(shots*iteration))
    fig = plt.figure()
    plt.xlabel("position")
    plt.ylabel("probability")
    plt.xlim([-1, 2**(n)+1])
    plt.bar(kln_int, hel, width=0.8)
    #plt.show()
    tag = datetime.datetime.now()
    fig.savefig("./real/%squbits/real_%stimes%s" % (str(n), str(iteration), (str(tag.month)+str(tag.day)+str(tag.hour)+str(tag.minute)+str(tag.second))))
    # fig.show()
    print("This is %s qubits quantum walk" % str(n))
