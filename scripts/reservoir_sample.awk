#!/bin/awk -f 
#reservior program.default sample number is 1000
#uasge: awk -f reservior_sample.awk -vnumber=200 inputFile
BEGIN{
    sample_num = 1000
    if (number != "")
	sample_num = number
    srand()
}
NR <= sample_num {
  reserve[NR]=$0
}
NR > sample_num{
  seed = int(rand()* NR )
  if (seed < sample_num)
	reserve[seed+1] = $0
}
END{
    for(i=1;i<=sample_num;i++)
	print reserve[i]

}