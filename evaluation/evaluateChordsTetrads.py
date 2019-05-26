#!/usr/bin/env python
'''
Chris Miller
cmiller@di.ens.fr

evaluates chord recognition by all chord qualities using MIREX

usage: 
        ./evaluateChordsMirex.py -o output_file filelist /path/to/results/ 
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

   # initialize chord list
   chord_list = [ 'maj', 'min', 'min7', '7', 'N', 'maj7', 'sus4', 'maj6', 'min6', 'sus2', 'dim', 'aug', 'hdim7', 'dim7']
   # initialize ordered dictionary containing tetrad scores by chord quality
   scores_by_chord = collections.OrderedDict()

   #########################################################################################
   # loop through chord qualities
   for chordType in chord_list:

       # open filelist and build list of files used in experiment
       f = open(refFilename)
       filelist = f.readlines()
       f.close()

       # counter for tetrad_scores array
       counter = 0;
       tetrad_scores = []

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
        
            # build index arrays over whole track and sync to reference
            full_ref_idx = np.array([ref_starts, ref_ends]).T
            full_est_idx = np.array([est_starts, est_ends]).T

            e_int, e_lbl = mir_eval.util.adjust_intervals(full_est_idx, est_labels, full_ref_idx.min(), full_ref_idx.max(),'N', 'N')
            intervals, r_lbl, e_lbl = mir_eval.util.merge_labeled_intervals(full_ref_idx, ref_labels, e_int, e_lbl)


            #########################################################
            # filter by chordType

            filtered_ref_starts = []
            filtered_ref_ends = []
            filtered_est_starts = []
            filtered_est_ends = []
            filtered_ref_labels = []
            filtered_est_labels = []

            # loop through reference arrays
            for i in range(len(r_lbl)):
                 if chordType == 'N':
                    currentChordQuality = r_lbl[i]
                 else:
                    currentChordQuality = mir_eval.chord.split(r_lbl[i])[1]

                 if currentChordQuality == chordType:
                    filtered_ref_starts.append(intervals[i,0])
                    filtered_ref_ends.append(intervals[i,1])
                    filtered_ref_labels.append(r_lbl[i])
                    filtered_est_labels.append(e_lbl[i])

            # compute scores and grab tetrad for averaging
            filtered_ref_idx = np.array([filtered_ref_starts, filtered_ref_ends]).T
            durations = mir_eval.util.intervals_to_durations(filtered_ref_idx)
            try:
                weighted_score = mir_eval.chord.weighted_accuracy(mir_eval.chord.tetrads(filtered_ref_labels, filtered_est_labels), durations)
                tetrad_scores.append(weighted_score)
                counter += 1
            except ValueError as error:
                pass
            except TypeError as error:
                pass

       #########################################################################################
       #  average tetrad_scores
       mu = np.mean(tetrad_scores)
       
       # store in results dict
       scores_by_chord[chordType] = mu

       status = 'There are ' + str(len(tetrad_scores)) + ' tracks with ' + chordType + ' in test set.'
       print(status)

   #########################################################################################

   print("{} vs. {}".format(os.path.basename(parameters['referenceList']),
                             os.path.basename(parameters['estimatedDir'])))

   print_evaluation(scores_by_chord)

   if parameters['output_file']:
      print('Saving results to: ', parameters['output_file'])
      save_results(scores_by_chord, parameters['output_file'])
