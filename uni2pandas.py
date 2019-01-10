#!/usr/bin/env python

import click as ck
import numpy as np
import pandas as pd
import gzip
import logging
from utils import GeneOntology, is_exp_code

logging.basicConfig(level=logging.INFO)

@ck.command()
@ck.option(
    '--go-file', '-gf', default='data/go.obo',
    help='Gene Ontology file in OBO Format')
@ck.option(
    '--uniprot-file', '-uf', default='data/uniprot_sprot.dat.gz',
    help='UniProt knowledgebase file in text format (archived)')
@ck.option(
    '--filter_exp', '-fe', is_flag=True,
    help='Filter proteins with experimental annotations')
@ck.option(
    '--prop-annots', '-pa', is_flag=True,
    help='Propagate annotations with GO structure')
@ck.option(
    '--out-file', '-o', default='data/swissprot.pkl',
    help='Result file with a list of proteins, sequences and annotations')
def main(go_file, uniprot_file, filter_exp, prop_annots, out_file):
    go = GeneOntology(go_file, with_rels=True)

    proteins, accessions, sequences, annotations = load_data(uniprot_file)
    df = pd.DataFrame({
        'proteins': proteins,
        'accessions': accessions,
        'sequences': sequences,
        'annotations': annotations
    })

    if filter_exp:
        logging.info('Filtering proteins with experimental annotations')
        index = []
        annotations = []
        for i, row in df.iterrows():
            annots = []
            for annot in row['annotations']:
                go_id, code = annot.split('|')
                if is_exp_code(code):
                    annots.append(go_id)
            # Ignore proteins without experimental annotations
            if len(annots) == 0:
                continue
            index.append(i)
            annotations.append(annots)
        df = df.loc[index]
        df = df.reset_index()
        df['annotations'] = annotations
        
    if prop_annots:
        prop_annotations = []
        for i, row in df.iterrows():
            # Propagate annotations
            annot_set = set()
            annots = row['annotations']
            for go_id in annots:
                go_id = go_id.split('|')[0] # In case if it has code
                annot_set |= go.get_anchestors(go_id)
            annots = list(annot_set)
            prop_annotations.append(annots)
        df['annotations'] = prop_annotations
    
    df.to_pickle(out_file)
    logging.info('Successfully saved %d proteins' % (len(df),) )
    
def load_data(uniprot_file):
    proteins = list()
    accessions = list()
    sequences = list()
    annotations = list()
    with gzip.open(uniprot_file, 'rt') as f:
        prot_id = ''
        prot_ac = ''
        seq = ''
        annots = list()
        for line in f:
            items = line.strip().split('   ')
            if items[0] == 'ID' and len(items) > 1:
                if prot_id != '' and len(annots) > 0:
                    proteins.append(prot_id)
                    accessions.append(prot_ac)
                    sequences.append(seq)
                    annotations.append(annots)
                prot_id = items[1]
                annots = list()
                seq = ''
            elif items[0] == 'AC' and len(items) > 1:
                prot_ac = items[1]
            elif items[0] == 'DR' and len(items) > 1:
                items = items[1].split('; ')
                if items[0] == 'GO':
                    go_id = items[1]
                    code = items[3].split(':')[0]
                    annots.append(go_id + '|' + code)
            elif items[0] == 'SQ':
                seq = next(f).strip().replace(' ', '')
                while True:
                    sq = next(f).strip().replace(' ', '')
                    if sq == '//':
                        break
                    else:
                        seq += sq


        if len(annots) > 0:
            proteins.append(prot_id)
            accessions.append(prot_ac)
            sequences.append(seq)
            annotations.append(annots)
    return proteins, accessions, sequences, annotations


if __name__ == '__main__':
    main()
