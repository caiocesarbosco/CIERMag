#!/bin/bash

file1=./run_script_temp.sh
file2=./files/sensordatafile.txt

if [ -f "$file1" ]; then
	sudo rm ./run_script_temp.sh	
else
	echo "temp_file doesnt exist."
fi

if [ -f "$file2" ]; then
	sudo rm ./files/sensordatafile.txt
else
	echo "sensordatafile.txt doesnt exist"
fi

a=$(ps -fA | grep rpi_main | awk 'NR==1{print $2}')

while [ -n "$a" ]
do
	echo "#!/bin/bash" >> ./run_script_temp.sh
	echo -n "sudo kill -9 " >> ./run_script_temp.sh
	echo "$a" >> ./run_script_temp.sh
	sudo chmod +sx ./run_script_temp.sh
	./run_script_temp.sh
	a=$(ps -fA | grep rpi_main | awk 'NR==1{print $2}')  
	b=$(ps -fA | grep rpi_main | wc -l)
        sudo rm ./run_script_temp.sh

	if [ "$b" = "1" ]; then
		break
	else
		echo
	fi
done
python ./rpi_main.py




