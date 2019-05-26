#!/usr/bin/env python
'''
Chris Miller
cmiller@di.ens.fr

basic evaluator for chord recognition

usage: 
        ./basic_evaluate.py -o results.json filelist.txt /path/to/results/
                                                                         ^ -- this slash is important

'''

from __future__ import print_function
import json
import numpy as np
import os
import argparse
import sys

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

   # open filelist and build list of files used in experiment
   f = open(refFilename)
   filelist = f.readlines()
   f.close()

   for track in filelist:
        # parse filelist, finding reference annotations and estimated results
        track = track.strip()
        (refDir, refFile) = os.path.split(track)
        (name, ext) = os.path.splitext(refFile)
        referenceFilename = refDir + '/' + name + '.lab'
        estimatedFilename = estDir + name + ext + '.txt'

        # load data and concat into large arrays
        init = 1
        if init:
           (ref_idx, ref_labels) = mir_eval.io.load_labeled_intervals(referenceFilename)
           (est_idx, est_labels) = mir_eval.io.load_labeled_intervals(estimatedFilename)
           init = 0
        else:
           (temp_ref_idx, temp_ref_labels) = mir_eval.io.load_labeled_intervals(referenceFilename)
           (temp_est_idx, temp_est_labels) = mir_eval.io.load_labeled_intervals(estimatedFilename)

           ref_idx = np.append(ref_idx, temp_ref_idx, axis=0)
           est_idx = np.append(est_idx, temp_est_idx, axis=0)
           ref_labels = ref_labels + temp_ref_labels
           est_labels = est_labels + temp_est_labels

   # compute scores and write to json file
   scores = mir_eval.chord.evaluate(ref_idx, ref_labels, est_idx, est_labels)

   if parameters['output_file']:
      print('Saving results to: ', parameters['output_file'])
      save_results(scores, parameters['output_file'])
