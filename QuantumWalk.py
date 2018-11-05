from qiskit import IBMQ, QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, Aer
from qiskit.qasm import pi
from qiskit.tools.visualization import plot_histogram, circuit_drawer
import numpy as np

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

    def _QFT(self):
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


    def _QFT_dg(self):
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
        circuit_drawer(qc).show()


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
        qc.u3(0.4, 0, 0, q[0])
        # qc.x(q[0])
        for i in range(2, self.qubits):
            qc.x(q[i])

        self._QFT_dg()
        self._S_plus()
        self._QFT()

        qc.cx(q[1], q[0])
        qc.u3(0.4+pi, 0, 0, q[0])
        qc.cx(q[1], q[0])

        self._QFT_dg()
        self._S_minus()
        self._QFT()

        qc.measure(q, c)
        backends = ['ibmq_20_tokyo', 'qasm_simulator',  'ibmqx_hpc_qasm_simulator']

        backend_sim = IBMQ.get_backend(backends[2])
        # backend_sim = Aer.get_backend(backends[1])

        result = execute(qc, backend_sim, shots=4096).result()

        print(qc.qasm())
        circuit_drawer(qc).show()
        plot_histogram(result.get_counts(qc))

        print(result.get_counts(qc))




if __name__ == '__main__':
    a = QuantumWalk(0, 5, 5, 5)
    # a._QFT()
    a._QFT_dg_fixing()
    # a._S_plus()
    # a._S_minus()
    # a.walk()
