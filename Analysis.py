import scrapy, dill, os, operator, sys
from pprint import pprint, pformat
import matplotlib.pyplot as plt
from collections import OrderedDict
import numpy as np
from weasyprint import HTML
import dominate
from dominate.tags import *
from dominate import tags
import sys, getopt, argparse

with open('supplement metallmind', 'rb') as f:
    supplement_metallmind = dill.load(f)

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def outcome_frequencies():
    frequencies = dict()

    for supplement in supplement_metallmind.values():
        for outcome in supplement['outcomes'].keys():
            if outcome in frequencies.keys():
                frequencies[outcome] += 1
            else:
                frequencies[outcome] = 1

    return frequencies

ordered_outcome_frequencies = lambda: sorted(outcome_frequencies().items(), key=lambda x: x[1])

def plot_outcome_frequencies(n=32):

    frequencies = np.asarray(ordered_outcome_frequencies()[-n:])

    x = range(frequencies.shape[0])
    plt.bar(x, frequencies[:, 1].astype(int), align='center')
    plt.xticks(x, frequencies[:, 0], rotation=45)

    plt.show()

def supplements_for_outcome(outcome):
    supplements = dict()

    for supplement in supplement_metallmind.keys():
        if outcome in supplement_metallmind[supplement]['outcomes'].keys():
            supplements[supplement] = supplement_metallmind[supplement]

    return supplements

def best_supplements_for_outcome(outcome, n=10):
    supplements = supplements_for_outcome(outcome)

    key = lambda x: np.prod([v for v in x[1]['outcomes'][outcome].values() if isinstance(v, int)])

    best_supplements = sorted(supplements.items(), key=key)

    if n > 0:
        return best_supplements[-min(n, len(best_supplements)):]
    elif n < 0:
        return best_supplements[:min(abs(n), len(best_supplements))]
    else:
        raise ValueError('n may not equal zero')

def report(supplement, outcome, p=False, show=False):

    supplement_name = supplement.replace('-', ' ')
    outcome_name = outcome.replace('-', ' ')
    title='Report on the effects of {} with respect to {}'.format(supplement_name, outcome_name)
    fname = 'reports/{}.pdf'.format(title)
    doc = dominate.document(title=title)

    # with doc.head:
    #     link(rel='stylesheet', href='style.css')
    #     script(type='text/javascript', src='script.js')

    summary = str(pformat(supplement_metallmind[supplement]['summary'].replace('\n', ' ')))[2:-1]
    outcome = supplement_metallmind[supplement]['outcomes'][outcome]
    grade_info = 'level of evidence: {}'.format(outcome['grade'])
    magnitude_info = 'magnitude of effect: {}'.format(outcome['magnitude'])
    consistency_info = 'consistency of research results: {}'.format(outcome['consistency'])
    notes = outcome['notes']

    doc += h1(title)
    doc += h2('Summary')
    doc += tags.p(summary)
    doc += h2('Effects on {}'.format(outcome_name))
    doc += tags.p(grade_info)
    doc += tags.p(magnitude_info)
    doc += tags.p(consistency_info)
    if notes is not None:
        doc += h3('notes')
        doc += tags.p(notes)

    HTML(string=str(doc)).write_pdf(fname)
    if show:
        os.system('xpdf {}'.format(fname.replace(' ', '\ ')))
    if p:
        os.system('lp {}'.format(fname.replace(' ', '\ ')))

def make_reports_on_outcomes(outcomes, prnt=False, show=True, n=6):

    if prnt:
        num_pages = len(outcomes) * abs(n)
        if not query_yes_no('are you sure you want to print {} pages?'.format(num_pages)):
            return

    for outcome in outcomes:
        best_supplements = best_supplements_for_outcome(outcome, n=n)
        for supplement in best_supplements:
            report(supplement[0], outcome, show=show, p=prnt)

if __name__ == '__main__':
    # frequencies = ordered_outcome_frequencies()
    # plot_outcome_frequencies()

    # outcomes = ['cognition', 'memory', 'lean-mass', 'power-output', 'subjective-well-being',
    #             'attention', 'reaction-time', 'motivation', 'processing-speed', 'processing-accuracy', 'working-memory']

    # outcomes = ['cognition']
    # make_reports_on_outcomes(
    #     outcomes=outcomes,
    #     p=False,
    #     n=16,
    #     show=True
    # )

    # make_reports_on_outcomes(['anxiety'], n=-5)

    parser = argparse.ArgumentParser(description='generate supplement reports', add_help=True)
    parser.add_argument('-o', action='append', dest='outcomes', default=[])
    parser.add_argument('-n', action='store', dest='n', default=2, type=int)
    parser.add_argument('-s', action='store_true', dest='show', default=False)
    parser.add_argument('-p', action='store_true', dest='prnt', default=False)

    args = vars(parser.parse_args())

    make_reports_on_outcomes(outcomes=args['outcomes'], n=args['n'], show=args['show'], prnt=args['prnt'])

