#!/bin/bash

max=$1
t=$2

date=$(date +%Y-%m-%d_%H-%M-%S)
output_file="../test/instances_$max-w_$t-t_$date.csv"

echo "weeks,groups,participants,model,symmetry_breaking,all_solutions,solutions,time,timed_out" > "$output_file"

for w in $(seq 1 "$max") ; do
  for g in $(seq 1 "$w") ; do
    for p in $(seq 1 "$w") ; do
      if [[ "$w" < $(( g*p )) ]] || { [[ "$g" == "$w" ]] && [[ "$p" == 1 ]]; } ; then
        for m in {1..3} ; do
          for s in true false ; do
            for a in true false ; do
              if [[ "$s" == true ]] && [[ "$a" == true ]] ; then
                exec=$(python ./main.py -w "$w" -g "$g" -p "$p" -m "$m" -s -a -t "$t" -l)
              elif [[ "$s" == true ]] && [[ "$a" == false ]] ; then
                exec=$(python ./main.py -w "$w" -g "$g" -p "$p" -m "$m" -s -t "$t" -l)
              elif [[ "$s" == false ]] && [[ "$a" == true ]] ; then
                exec=$(python ./main.py -w "$w" -g "$g" -p "$p" -m "$m" -a -t "$t" -l)
              else
                exec=$(python ./main.py -w "$w" -g "$g" -p "$p" -m "$m" -t "$t" -l)
              fi

              solutions=$(echo "$exec" | grep "solutions:" | cut -d' ' -f4)
              time=$(echo "$exec" | grep "time:" | cut -d' ' -f3)
              timed_out=$(echo "$exec" | grep "Timeout reached:")

              if [[ "$timed_out" == "Timeout reached:" ]] ; then
                timed_out=true
              else
                timed_out=false
              fi

              echo "$w $g $p $m $s $a $solutions $time $timed_out"
              echo "$w,$g,$p,$m,$s,$a,$solutions,$time,$timed_out" >> "$output_file"
            done
          done
        done
      fi
    done
  done
done
