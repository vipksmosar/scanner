# scanner


To start port scanner.

Linux:
python3 scanner.py --filein 'file_example_in.xlsx'  --ports 22 139 445 5060 --OneHost 1

or if many hosts - without parametr OneHost:

python3 portscanner.py --filein 'file_example_in.xlsx' --fileout 'file_example_out.csv' --IPcol 'IP' --ports 22 139 445 5060

Windows:

python.exe scanner.py --filein 'file_example_in.xlsx' --ports 22 139 445 5060 --OneHost 1

or if many hosts - without parametr OneHost:

python.exe portscanner.py --filein 'file_example_in.xlsx' --ports 22 139 445 5060

If you want to start ping.


Linux:

python3 scanner.py --filein 'file_example_in.xlsx'  --Ping True

Windows:

python.exe scanner.py --filein 'file_example_in.xlsx'  --Ping True




For more parametrs use --help
--filein 'C:/CSV/srv_vm2.xlsx'
--ports 20 21 22 139 445 80 44
--ports_range 20 25
--ip_range 192.168.10.23-192.168.10.25
--IPcol 'IP' - default 'IP'
--OneHost True - default False
--Ping True - default False
--fileout 'C:/CSV/HOSTS_VIRT_withScanned.csv' - default 'out_file.csv'

