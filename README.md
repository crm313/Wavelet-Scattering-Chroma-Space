# Wavelet-Scattering-Chroma-Space
Wavelet Scattering in Chroma Space

ABSTRACT:
State of the art automatic chord recognition systems rely on multiband chroma representations, Gaussian Mixture Model pattern matching, and Viterbi decoding. This thesis explores the use of Haar wavelet transforms and scattering in place of multiband chroma. Wavelets operating across octaves encode sums and differences in chroma bins at different scales. We describe both the Haar wavelet transform and deep wavelet scattering and develop an efficient algorithm for their computation. Potential benefits of wavelet representations, including stability to octave deformations, over multiband chroma are discussed. Accuracy of wavelet representations used for chord recognition is analyzed over a large vocabulary of chord qualities.

Repository contains code implementing and evaluating the above-described chord recognition system. 

Data used comes from MedleyDB - https://medleydb.weebly.com/

Evaluation uses mir_eval package https://craffel.github.io/mir_eval/#id2
