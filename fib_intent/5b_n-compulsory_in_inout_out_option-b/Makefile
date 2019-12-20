

sig:
	python -m numpy.f2py -m fibonacci -h fib.pyf --overwrite-signature fib.f90

lib:
	python -m numpy.f2py -c fib_mod.pyf fib.f90
	rm -rf *.dSYM

clean:
	rm -rf *.pyf *.so
