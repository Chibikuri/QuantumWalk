from qiskit import IBMQ, QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, Aer
from qiskit.qasm import pi
from qiskit.tools.visualization import plot_histogram, circuit_drawer
import numpy as np
import matplotlib.pyplot as plt
import sys

IBMQ.load_accounts()
IBMQ.backends()

class QuantumWalk:

    def __init__(self, initial, qubits, cbits, n):
        self.initial = initial
        self.qubits = qubits
        self.cbits = cbits
        self.n = n
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
        # circuit_drawer(qc).show()

    def _QFT_fixing(self):
        q = self.q
        qc = self.qc
        for n in range(1, self.qubits-1):
            qc.h(q[n])
            # print(n)
            for t in range(1, n):
                try:
                    qc.cu1(pi/(2**(t)), q[n], q[t+n])
                    # print(pi/(2**(t)), n, t+n)
                except:
                    continue

        qc.h(q[self.qubits-1])
        # circuit_drawer(qc).show()





    def _QFT(self):
        q = self.q
        qc = self.qc
        qc.h(q[self.qubits-1])
        for m in range(self.qubits-2, 0, -1):
            # print(m)
            for u in range(self.qubits, 0, -1):
                try:
                    qc.cu1(pi/(2**(u)), q[u+m], q[m])
                    # print(pi/(2**(u)), u+m, m)
                except:
                    continue
            qc.h(q[m])
        # circuit_drawer(qc).show()

    def _QFT_dg_fixing(self):
        q = self.q
        qc = self.qc
        for m in range(1, self.qubits-1):
            qc.h(q[m])
            print(m)
            for u in range(1, self.qubits):
                try:
                    qc.cu1(pi/(2**(u)), q[u+m], q[m])
                    print(pi/(2**(u)), u+m, m)
                except:
                    continue
        # circuit_drawer(qc).show()


    def _S_plus(self):
        q = self.q
        qc = self.qc
        coef = sum([1/2**i for i in range(2, self.qubits+1)])
        for i in range(1, self.qubits):
            qc.cx(q[0], q[i])
            qc.u1(-pi/2**(i+1), q[0])
            qc.cx(q[0], q[i])
        qc.u1(coef*pi, q[0])
        for j in range(self.qubits-1):
            qc.u1(-pi/2**(self.qubits-j), q[j])
            # print(2**(self.qubits-j))


    def _S_minus(self):
        q = self.q
        qc = self.qc
        coef = sum([1/2**i for i in range(2, self.qubits+1)])
        for i in range(1, self.qubits):
            qc.cx(q[0], q[i])
            qc.u1(-pi/2**(i+1), q[0])
            qc.cx(q[0], q[i])
        qc.u1(coef*pi, q[0])
        for j in range(self.qubits-1):
            qc.u1(pi/2**(self.qubits-j), q[j])
            # print(2**(self.qubits-j))

    def walk(self):
        c = self.c
        q = self.q
        qc = self.qc
        #initial coin operator
        qc.cx(q[1], q[0])
        qc.u3(0.4, 0, 0, q[0])
        qc.cx(q[1], q[0])
        # qc.h(q[0])
        for i in range(2, self.qubits):
            qc.x(q[i])

        # step operator
        self._QFT_dg()
        self._S_plus()
        self._QFT()

        #initial coin operator2
        qc.cx(q[1], q[0])
        qc.u3(0.4+pi, 0, 0, q[0])
        # qc.h(q[0])
        qc.cx(q[1], q[0])

        #step operator
        self._QFT_dg()
        self._S_minus()
        self._QFT()
        for i in range(1, self.qubits):
            qc.measure(q[i], c[i-1])
        # qc.measure(q, c)
        backends = ['ibmq_20_tokyo', 'qasm_simulator',  'ibmqx_hpc_qasm_simulator']

        backend_sim = IBMQ.get_backend(backends[2])
        # backend_sim = Aer.get_backend(backends[1])

        result = execute(qc, backend_sim, shots=8192).result()


        m = result.get_counts(qc)
        keys = [int(k, 2) for k in m.keys()]
        values = [l/8192 for l in m.values()]

        print(qc.qasm())
        # circuit_drawer(qc).show()
        # plot_histogram(result.get_counts(qc))
        # print(values[1022])
        # print(values[1023])
        # print(values[1024])
        # print(values[1025])
        # print(values[1026])
        # print(values[1027])
        plt.xlabel("position")
        plt.ylabel("probability")
        plt.bar(keys, values, width=0.8)
        plt.show()

        print(result.get_counts(qc))

    def check(self):
        c = self.c
        q = self.q
        qc = self.qc
        # for i in range(1, self.qubits-1):
        #     qc.x(q[i])
        qc.x(q[2])
        self._QFT()
        # self._QFT_dg()
        qc.measure(q, c)
        backends = ['ibmq_20_tokyo', 'qasm_simulator',  'ibmqx_hpc_qasm_simulator']

        backend_sim = IBMQ.get_backend(backends[2])
        # backend_sim = Aer.get_backend(backends[1])

        result = execute(qc, backend_sim, shots=4096).result()

        print(qc.qasm())
        circuit_drawer(qc).show()
        plot_histogram(result.get_counts(qc))

        print(result.get_counts(qc))

    def check_parity(self):
        c = self.c
        q = self.q
        qc = self.qc


        qc.h(q[1])
        qc.u1(pi/4, q[1])
        qc.u1(pi/4, q[2])
        qc.cx(q[1], q[2])
        qc.u1(-pi/4, q[2])
        qc.cx(q[1], q[2])
        qc.h(q[2])
        qc.measure(q, c)
        backends = ['ibmq_20_tokyo', 'qasm_simulator',  'ibmqx_hpc_qasm_simulator']

        backend_sim = IBMQ.get_backend(backends[2])
        # backend_sim = Aer.get_backend(backends[1])
        result = execute(qc, backend_sim, shots=4096).result()
        circuit_drawer(qc).show()
        print(result.get_counts(qc))

        qb = QuantumRegister(self.qubits)
        cb = ClassicalRegister(self.cbits)
        qcb = QuantumCircuit(qb, cb)


        qcb.h(qb[2])
        qcb.cu1(pi/2, qb[2], qb[1])
        qcb.h(qb[1])
        qcb.measure(qb, cb)

        backends = ['ibmq_20_tokyo', 'qasm_simulator',  'ibmqx_hpc_qasm_simulator']

        backend_sim = IBMQ.get_backend(backends[0])
        # backend_sim = Aer.get_backend(backends[1])
        result_b = execute(qcb, backend_sim, shots=4096).result()

        circuit_drawer(qcb).show()


        print(result_b.get_counts(qcb))

if __name__ == '__main__':
    a = QuantumWalk(0, 10, 19, 5)
    # a._QFT_dg()
    # a._QFT_fixing()
    # a._QFT_dg_fixing()
    # a._S_plus()
    # a._S_minus()
    a.walk()
    # a.check()
    # a._QFT()
    # a.check_parity()
