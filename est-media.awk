#!/usr/bin/awk -f
#
#     Compute average and standard deviation
#----------------------------------------------------------

{
   soma+=$1
   somaquad+=$1*$1
}

END {
       media=soma/NR
       desvpad=sqrt((somaquad - NR*media**2)/(NR - 1))
       	if(media != 0 ){desvpadper=desvpad/media*100}else{devpadper=0}
      printf "%.8f\n", \
              media
    }
