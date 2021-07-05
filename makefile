# coquetterie
ifeq (run,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "run"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

# sudo apt-get install valgrind kcachegrind
# pip install pyprof2calltree

#Visualization 1:
all: run

run: profile
	kcachegrind profile_data.pyprof.log

profile:
	python3 -m cProfile -o profile_data.pyprof $(RUN_ARGS).py
	pyprof2calltree -i profile_data.pyprof # this converts the stats into a callgrind format

#Visualization 2:
# pip install gprof2dot
visu2:
	gprof2dot --format=callgrind --output=out.dot profile_data.pyprof.log
	dot -Tsvg out.dot -o graph.svg

clean:
	rm -f profile_data.pyprof profile_data.pyprof.log graph.svg out.dot