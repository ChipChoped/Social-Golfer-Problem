#!/bin/bash

max=$1
t=$2

date=$(date +%Y-%m-%d_%H-%M-%S)
output_dir="../test/"
output_file="${output_dir}instances_solver_$max-w_$t-t_$date.csv"

mkdir -p "$output_dir"

echo "weeks,groups,participants,solution,time,timed_out,valid" > "$output_file"

for w in $(seq 1 "$max") ; do
  for g in $(seq 1 "$w") ; do
    for p in $(seq 1 "$w") ; do
#      if [[ "$w" < $(( g*p )) ]] || { [[ "$g" == "$w" ]] && [[ "$p" == 1 ]]; } ; then
        #for m in {1..3} ; do
          for s in true ; do
            #for a in true false ; do
              if [[ "$s" == true ]] && [[ "$a" == true ]] ; then
                exec=$(python3 ./custom_solver.py -w "$w" -g "$g" -p "$p" -s -t "$t" -c)
              elif [[ "$s" == true ]] && [[ "$a" == false ]] ; then
                exec=$(python3 ./custom_solver.py -w "$w" -g "$g" -p "$p" -s -t "$t" -c)
              elif [[ "$s" == false ]] && [[ "$a" == true ]] ; then
                exec=$(python3 ./custom_solver.py -w "$w" -g "$g" -p "$p" -t "$t" -c)
              else
                exec=$(python3 ./custom_solver.py -w "$w" -g "$g" -p "$p" -t "$t" -c)
              fi

              solution=$(echo "$exec" | grep "No solution found")
              time=$(echo "$exec" | grep "time:" | cut -d' ' -f3)
              timed_out=$(echo "$exec" | grep "Timeout reached")
              valid=$(echo "$exec" | grep "is valid")

              if [[ "$solution" == "No solution found" ]] ; then
                solution=false
              else
                solution=true
              fi

              if [[ "$timed_out" == "Timeout reached" ]] ; then
                timed_out=true
                solution=false
              else
                timed_out=false
              fi

              if [[ "$valid" == "The schedule is valid" ]] ; then
                valid=true
              else
                valid=false
              fi

              echo "$w $g $p $solution $time $timed_out $valid"
              echo "$w,$g,$p,$solution,$time,$timed_out,$valid" >> "$output_file"
            #done
          done
        #done
#      fi
    done
  done
done