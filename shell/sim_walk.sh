for i in `seq 1 4`
do
	python QuantumWalk.py 3 $i
done
for i in `seq 1 8`
do
	python QuantumWalk.py 4 $i
done
python notification.py
