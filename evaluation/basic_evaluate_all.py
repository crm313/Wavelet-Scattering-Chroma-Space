#!/usr/bin/env python
'''
Chris Miller
cmiller@di.ens.fr

evaluates chord recognition overall by all metrics

usage: 
        ./basic_evaluate_all.py -o output_file filelist /path/to/results/ 
                                                                        ^ -- this slash is important

parameters:
        - output_file : str
            Path to .json file to write to
        - filelist : str
            Path to .txt file containing filepaths to data used in testing set
        - results : dict
            Results dictionary, where keys are metric names and values are
            the corresponding scores
'''

from __future__ import print_function
from future.utils import iteritems
import json
import numpy as np
import os
import argparse
import sys
import collections

import mir_eval

def save_results(results, output_file):
    '''
    Write a result dictionary out as a .json file.

    :parameters:
        - results : dict
            Results dictionary, where keys are metric names and values are
            the corresponding scores
        - output_file : str
            Path to .json file to write to
    '''
    with open(output_file, 'w') as f:
        json.dump(results, f)


def print_evaluation(results):
    '''
    Print out a results dict.

    :parameters:
        - results : dict
            Results dictionary, where keys are metric names and values are
            the corresponding scores
    '''
    max_len = max([len(key) for key in results])
    for key, value in iteritems(results):
        if type(value) == float:
            print('\t{:>{}} : {:.3f}'.format(key, max_len, value))
        else:
            print('\t{:>{}} : {}'.format(key, max_len, value))

def process_arguments():
    '''Argparse function to get the program parameters'''

    parser = argparse.ArgumentParser(description='mir_eval chord evaluation')

    parser.add_argument('-o',
                        dest='output_file',
                        default=None,
                        type=str,
                        action='store',
                        help='Store results in json format')

    parser.add_argument('referenceList',
                        action='store',
                        help='path to wav files estimated')

    parser.add_argument('estimatedDir',
                        action='store',
                        help='path to the estimated results')

    return vars(parser.parse_args(sys.argv[1:]))


if __name__ == '__main__':

   # Get the parameters
   parameters = process_arguments()
   refFilename = parameters['referenceList']
   estDir = parameters['estimatedDir']

   # initialize lists and dicts
   scores = {}
   mirex = []
   root = []
   tetrads = []
   majmin = []
   triads = []
   thirds = []
   sevenths = []
   tetrads_inv = []
   majmin_inv = []
   triads_inv = []
   thirds_inv = []
   sevenths_inv = []

   #########################################################################################

   # open filelist and build list of files used in experiment
   f = open(refFilename)
   filelist = f.readlines()
   f.close()

   # counter 
   counter = 0;

   #########################################################################################
   #  loop through tracks in filelist

   for track in filelist:
        # parse filelist, finding reference annotations and estimated results
        track = track.strip()
        (refDir, refFile) = os.path.split(track)
        (name, ext) = os.path.splitext(refFile)
        referenceFilename = refDir + '/' + name + '.lab'
        estimatedFilename = estDir + name + '.wav.txt'

        # load labels in reference/estimated files
        (ref_idx, ref_labels) = mir_eval.io.load_labeled_intervals(referenceFilename)
        (est_idx, est_labels) = mir_eval.io.load_labeled_intervals(estimatedFilename)

        # compute scores and store individual metrics in numpy array
        scores = mir_eval.chord.evaluate(ref_idx, ref_labels, est_idx, est_labels)
        mirex.append(scores['mirex'])
        root.append(scores['root'])
        tetrads.append(scores['tetrads'])
        majmin.append(scores['majmin'])
        triads.append(scores['triads'])
        thirds.append(scores['thirds'])
        sevenths.append(scores['sevenths'])
        tetrads_inv.append(scores['tetrads_inv'])
        majmin_inv.append(scores['majmin_inv'])
        triads_inv.append(scores['triads_inv'])
        thirds_inv.append(scores['thirds_inv'])
        sevenths_inv.append(scores['sevenths_inv'])

   #########################################################################################
   #  average scores and store in dict
   
   results = {}
   results['mirex'] = np.mean(mirex)
   results['root'] = np.mean(root)
   results['tetrads'] = np.mean(tetrads)
   results['majmin'] = np.mean(majmin)
   results['triads'] = np.mean(triads)
   results['thirds'] = np.mean(thirds)
   results['sevenths'] = np.mean(sevenths)
   results['tetrads_inv'] = np.mean(tetrads_inv)
   results['majmin_inv'] = np.mean(majmin_inv)
   results['triads_inv'] = np.mean(triads_inv)
   results['thirds_inv'] = np.mean(thirds_inv)
   results['sevenths_inv'] = np.mean(sevenths_inv)

   #########################################################################################

   print("{} vs. {}".format(os.path.basename(parameters['referenceList']),
                             os.path.basename(parameters['estimatedDir'])))

   print_evaluation(results)

   if parameters['output_file']:
      print('Saving results to: ', parameters['output_file'])
      save_results(results, parameters['output_file'])
