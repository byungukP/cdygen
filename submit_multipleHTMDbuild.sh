#!/bin/bash 

#####################
# UPDATE PARAMETERS #
#####################

bash submit_htmd_buildSystem.sh /mnt/e/masif_docker/pmp/htmd/lists/pmp_low_auc.txt
bash submit_htmd_buildSystem.sh /mnt/e/masif_docker/pmp/htmd/lists/pmp_med_auc.txt
bash submit_htmd_buildSystem.sh /mnt/e/masif_docker/pmp/htmd/lists/pmp_high_auc.txt

# clean up
# rm -fr *.cpt *.gro \#* *.tpr

exit;
