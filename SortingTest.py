X_POS = 1
Y_POS = 0
TOP_LEFT = 0
import numpy as np
import copy

approx = [
np.array([[[ 58, 178]],[[105, 179]],[[104, 257]],[[ 57, 257]]]),
np.array([[[ 13, 178]],[[ 50, 179]],[[ 49, 258]],[[ 12, 257]]]), 
np.array([[[ 58,  93]],[[105,  94]],[[104, 171]],[[ 57, 170]]]), 
np.array([[[ 13,  93]],[[ 50,  94]],[[ 49, 171]],[[ 12, 170]]]), 
np.array([[[ 58,   9]],[[105,  10]],[[104,  86]],[[ 57,  85]]]), 
np.array([[[13,  9]], [[50, 10]],[[49, 86]],[[12, 85]]])]


sorted_list = copy.deepcopy(approx)

sorted_list.sort(key=lambda x: x[0][0][0])
sorted_list.sort(key=lambda x: x[0][0][1], reverse = True)



print (sorted_list)
	
