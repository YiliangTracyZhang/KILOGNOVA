#!/usr/bin/env python
'''
genetic correlation estimation with individual data and summary stats

KILOGNOVA

Created on 2020-10-25

@author: Yiliang Zhang
'''

import argparse, os.path, sys
import pandas as pd
import numpy as np
from prep import prep
from ldsc_thin import ldscore, ggrscore
from calculate import calculate


try:
    x = pd.DataFrame({'A': [1, 2, 3]})
    x.drop_duplicates(subset='A')
except TypeError:
    raise ImportError('KILOGNOVA requires pandas version > 0.15.2')


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('precision', 4)
pd.set_option('max_colwidth',1000)
np.set_printoptions(linewidth=1000)
np.set_printoptions(precision=4)


# returns whether the parent directory of path exists
def parent_dir_exists(path):
    return os.path.exists(os.path.abspath(os.path.join(path, os.pardir)))

def pipeline(args):
    pd.options.mode.chained_assignment = None

    # Sanity check args
    if not parent_dir_exists(args.out):
        raise ValueError('--out flag points to an invalid path.')

    print('Preparing files for analysis...')
    gwas_snps, reversed_alleles_ref, N2 = prep(args.bfile, args.genotype, args.sumstats, args.N2)
    print('Calculating LD scores...')
    ld_scores, N1 = ldscore(args.bfile, args.genotype, args.phenotype, gwas_snps, reversed_alleles_ref)
    gwas_snps = gwas_snps[gwas_snps['SNP'].isin(ld_scores['SNP'])]
    print('{} SNPs included in our analysis...'.format(len(gwas_snps)))
    print('Calculating genetic covariance...')
    out = calculate(ld_scores, ggr_scores, y, N1, N2, args.h1, args.h2)
    out.to_csv(args.out, sep=' ', na_rep='NA', index=False)


parser = argparse.ArgumentParser()

parser.add_argument('phenotype',
    help='The individual-level phenotype data for the first trait.')
parser.add_argument('genotype',
    help='Prefix for Plink .bed/.bim/.fam file of individual-level genotype data for the first trait.')
parser.add_argument('sumstats',
    help='The sumstats file for the second trait.')

parser.add_argument('--bfile', required=True, type=str,
    help='Prefix for Plink .bed/.bim/.fam file of reference panel for the second trait.')
parser.add_argument('--h1', required=True, type=int,
    help='The estimated heritability of the first trait')
parser.add_argument('--h2', required=True, type=int,
    help='The estimated heritability of the second trait')
parser.add_argument('--N2', type=int,
    help='N of the sumstats file for the second trait. If not provided, this value will be inferred from the sumstats arg.')


parser.add_argument('--out', required=True, type=str,
    help='Location to output results.')

if __name__ == '__main__':
    pipeline(parser.parse_args())

