# coding: utf-8

# script to extract out ancestry segments from each reference population from admixed samples.
__author__ = 'egatkinson'

import argparse

"""
USAGE:
ExtractTracts.py --msp  <an ancestral calls file produced by RFmix version 2, suffixed with .msp.tsv>
                             --vcf <VCF file suffixed with .vcf>
"""

# input is expected to be a VCF file suffixed with .vcf and an ancestral calls file produced by RFmix version 2, suffixed with .msp.tsv

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msp', help='path stem to RFmix msp file, not including .msp.tsv', required=True)
    parser.add_argument('--vcf', help='path stem to RFmix input VCF with phased genotypes, not including .vcf suffix',
                        required=True)
    args = parser.parse_args()
    return (args)


args = parse_args()
mspfile = open(args.msp + '.msp.tsv', 'r')
genofile = open(args.vcf + '.vcf', 'r')
out0 = open(args.vcf + '.anc0.vcf', 'w')  # output for the extracted VCF anc 0
out1 = open(args.vcf + '.anc1.vcf', 'w')  # output for the extracted VCF anc 1
outdos0 = open(args.vcf + '.anc0.dosage.txt', 'w')  # output dosages for each ancestry into separate files
outdos1 = open(args.vcf + '.anc1.dosage.txt', 'w')  # output dosages for each ancestry into separate files
outancdos0 = open(args.vcf + '.anc0.hapcount.txt', 'w')  # output number of haplotype for each ancestry into separate files
outancdos1 = open(args.vcf + '.anc1.hapcount.txt', 'w')  # output number of haplotype for each ancestry into separate files

# initialize documenting the current window to check
chromosome = ("", 0, 0)

for line in genofile:
    if line.startswith("#"):
        out0.write(line)
        out1.write(line)
        continue
    if not line:
      break #stop when get to the end of the file
    CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT, genos = line.strip().split('\t', 9)
    genos = genos.replace('|', '\t').split('\t')  # split each strand geno call apart from each other
    output0 = '\t'.join([CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT])
    output1 = '\t'.join([CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT])
    outputdos0 = '\t'.join([CHROM, POS, ID])
    outputdos1 = '\t'.join([CHROM, POS, ID])
    outputancdos0 = '\t'.join([CHROM, POS, ID])
    outputancdos1 = '\t'.join([CHROM, POS, ID])
    POS = int(POS)

    # optimized for quicker runtime - only move to next line when out of the current msp window
    # save current line until out of window, then check next line. Input files should be in incremental order.
    while not (CHROM == chromosome[0] and (chromosome[1] <= POS < chromosome[2])):
        ancs = mspfile.readline()
        if ancs.startswith("#"):  # skip the header lines
            continue
        if not ancs:
            break  # when get to the end of the msp file, stop
        chm, spos, epos, sgpos, egpos, nsnps, calls = ancs.strip().split('\t', 6)
        calls = calls.split('\t')
        chromosome = (chm, int(spos), int(epos))

    for i in range(len(genos) // 2):
        # index by the number of individuals in the VCF file, should be the same number in the calls file
        genoA = str(genos[2 * i])
        genoB = str(genos[2 * i + 1])
        callA = str(calls[2 * i])
        callB = str(calls[2 * i + 1])
        count0 = 0
        count1 = 0
        count_anc0 = 0
        count_anc1 = 0

        # if the anc call is 0, keep, replace 1 or other calls with missing data
        if callA == '0':
            genoA0 = genoA
            genoA1 = "."
            count_anc0 = count_anc0 + 1  # tally up the ancestral haplotypes present at each site
            if genoA == '1':  # tally up counts of the minor/risk allele for each ancestry; technically the alternate allele here
                count0 = count0 + 1
        elif callA == '1':
            genoA0 = "."
            genoA1 = genoA  # if the anc call is 1, keep, otherwise make into missing data
            count_anc1 = count_anc1 + 1
            if genoA1 == '1':
                count1 = count1 + 1

        if callB == '0':
            genoB0 = genoB
            genoB1 = "."
            count_anc0 = count_anc0 + 1
            if genoB0 == '1':
                count0 = count0 + 1
        elif callB == '1':
            genoB0 = "."
            genoB1 = genoB
            count_anc1 = count_anc1 + 1
            if genoB1 == '1':
                count1 = count1 + 1

        output0 += '\t' + genoA0 + "|" + genoB0
        output1 += '\t' + genoA1 + "|" + genoB1
        outputdos0 += '\t' + str(count0)  
        # output the dosage for alt allele for each ancestry at each position for each indiv in the VCF file.
        outputdos1 += '\t' + str(count1)
        outputancdos0 += '\t' + str(count_anc0)
        outputancdos1 += '\t' + str(count_anc1)

    output0 += '\n'
    output1 += '\n'
    outputdos0 += '\n'
    outputdos1 += '\n'
    outputancdos0 += '\n'
    outputancdos1 += '\n'

    out0.write(output0)
    out1.write(output1)
    outdos0.write(outputdos0)
    outdos1.write(outputdos1)
    outancdos0.write(outputancdos0)
    outancdos1.write(outputancdos1)

out0.close()
out1.close()
outdos0.close()
outdos1.close()
outancdos0.close()
outancdos1.close()
