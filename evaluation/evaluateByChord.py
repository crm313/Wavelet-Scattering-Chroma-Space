#!/usr/bin/env python
'''
Chris Miller
cmiller@di.ens.fr

evaluates chord recognition by chord quality using MIREX

usage: 
        ./evaluateByChord.py -o output_file filelist /path/to/results/ chordType
                                                                     ^ -- this slash is important

parameters:
        - output_file : str
            Path to .json file to write to
        - filelist : str
            Path to .txt file containing filepaths to data used in testing set
        - results : dict
            Results dictionary, where keys are metric names and values are
            the corresponding scores
        - chordType : str
            Chord quality to filter on -- one of: 'maj', 'min', 'min7', '7', 'N', 'maj7', 'sus4',
                                                  'maj6', 'min6', 'sus2', 'dim', 'aug', 'hdim7', 'dim7'
'''

from __future__ import print_function
from future.utils import iteritems
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

    parser.add_argument('chordType',
                        action='store',
                        help='chord quality for filter')

    return vars(parser.parse_args(sys.argv[1:]))


if __name__ == '__main__':

   # Get the parameters
   parameters = process_arguments()
   refFilename = parameters['referenceList']
   estDir = parameters['estimatedDir']
   chordType = parameters['chordType']

   # open filelist and build list of files used in experiment
   f = open(refFilename)
   filelist = f.readlines()
   f.close()

   # counter for mirex_scores array
   counter = 0;
   mirex_scores = []

   #########################################################################################
   #  loop through tracks in filelist

   for track in filelist:
        # parse filelist, finding reference annotations and estimated results
        track = track.strip()
        (refDir, refFile) = os.path.split(track)
        (name, ext) = os.path.splitext(refFile)
        referenceFilename = refDir + '/' + name + '.lab'
        estimatedFilename = estDir + name + '.wav.txt'

        # load starts, ends, and labels in reference/estimated files
        ref_starts, ref_ends, ref_labels = mir_eval.io.load_delimited(referenceFilename, [float, float, str], r'\s+')
        est_starts, est_ends, est_labels = mir_eval.io.load_delimited(estimatedFilename, [float, float, str], r'\s+')

        #########################################################
        # filter by chordType

        filtered_ref_starts = []
        filtered_ref_ends = []
        filtered_est_starts = []
        filtered_est_ends = []
        filtered_ref_labels = []
        filtered_est_labels = []

        # loop through reference arrays
        for i in range(len(ref_labels)):
             currentChordQuality = mir_eval.chord.split(ref_labels[i])[1]
             if currentChordQuality == chordType:
                filtered_ref_starts.append(ref_starts[i])
                filtered_ref_ends.append(ref_ends[i])
                filtered_ref_labels.append(ref_labels[i])

        # loop through estimated arrays
        for i in range(len(est_labels)):
             currentChordQuality = mir_eval.chord.split(est_labels[i])[1]
             if currentChordQuality == chordType:
                filtered_est_starts.append(est_starts[i])
                filtered_est_ends.append(est_ends[i])
                filtered_est_labels.append(est_labels[i])
         
        # assemble interval labels from starts and ends
        filtered_ref_idx = np.array([filtered_ref_starts, filtered_ref_ends]).T
        filtered_est_idx = np.array([filtered_est_starts, filtered_est_ends]).T

        # Validate filtered intervals, and throw a warning in place of an error
        try:
            mir_eval.util.validate_intervals(filtered_ref_idx)
            mir_eval.util.validate_intervals(filtered_est_idx)
        except ValueError as error:
            warnings.warn(error.args[0])

        # compute scores and grab mirex for averaging
        scores = mir_eval.chord.evaluate(filtered_ref_idx, filtered_ref_labels, filtered_est_idx, filtered_est_labels)
        mirex_scores.append(scores['mirex'])
        counter += 1


   #########################################################################################
   #  average mirex_scores
   mu = np.mean(mirex_scores)

   print("{} vs. {}".format(os.path.basename(parameters['referenceList']),
                             os.path.basename(parameters['estimatedDir'])))
   print(mu)

   if parameters['output_file']:
      print('Saving results to: ', parameters['output_file'])
      save_results(mu, parameters['output_file'])
