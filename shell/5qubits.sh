for i in `seq 1 16`
do
	python QuantumWalk.py 5 $i
done
python notification.py

