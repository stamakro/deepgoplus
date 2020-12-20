
python diamond_data.py -df data/train_data.pkl -o data/train_data.fa 
python diamond_data.py -df data/test_data.pkl -o data/test_data.fa 


diamond makedb --in data/train_data.fa -d data/train_diamond_db #creates train_diamond_db.dmnd
 
diamond blastp  -d data/train_diamond_db.dmnd -t /tmp -q data/test_data.fa --outfmt 6 qseqid sseqid bitscore -o data/test_diamond.res


mkdir -p results

python evaluate_deepgoplus.py -o mf > results/deepgoplus_mf.txt #requires data/test_diamond.res
python evaluate_deepgoplus.py -o bp > results/deepgoplus_bp.txt
python evaluate_deepgoplus.py -o cc > results/deepgoplus_cc.txt


#python evaluate_diamondscore.py > results/diamondscore.txt