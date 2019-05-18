# -*- coding: utf-8 -*-
"""
@author: Cat Chenal
@module: LorenzGiniP
"""
__author__ = 'catchenal@gmail.com'
__doc__ = """
To obtain an 'augmented' Lorenz plot for a distribution and an associated measure;
The plot displays the Gini coefficient as well as the 'balanced inequality ratio, P'
(Kunegis and Preusse, doi:10.1145/2380718.238074).
Call: plot_lorenz_GP(xlor, ylor, x_measure = '', y_measure='income',
                   figw=6, show_caption=True, save_as='')
"""

import os
import numpy as np
from scipy.integrate import trapz

import matplotlib.pyplot as plt
from matplotlib import lines
from matplotlib.ticker import PercentFormatter


def findIntersection(sx, arr1, arr2, ax=None, c='red'):
    """
    Graphical approach to finding intersecting points (candidates)
    using arrays of points from two objects (e.g. a line, a curve).
    If no single match found, increase init_tol by step until at most
    two values are found within max_iter repetitions.
    P is plotted if found.
    """
    if ax is None:
        ax = plt.gca()
    
    # noise:
    noise_prec = 4
    eps1 = np.exp(np.random.randn(len(arr1))) * 10**-noise_prec
    eps2 = np.exp(np.random.randn(len(arr1))) * 10**-noise_prec
    
    y_anti = 1 - sx
    interps = np.interp(sx, arr1+eps1, arr2+eps2)
    py = np.argmin((interps - y_anti)**2)

    Py = interps[py]
    Px = 1 - Py
    
    ax.plot(Px, Py, marker='o', color=c, ms=4)    
    p_str = 'P ({:.1%},{:.1%})'.format(Px, Py)
    
    xoffset = -0.25 if Px > 0.9 else 0
    
    ax.text(Px+xoffset, Py+0.05,p_str,
             ha='center', fontsize=12)
    return Px, Py
    

def plot_lorenz_GP(xlor, ylor,
                   x_measure = '', y_measure='income',
                   figw=5,
                   show_caption=True,
                   save_as='', format='png'):
    """
    Wrapper to obtain an 'augmented' Lorenz plot for a distribution;
    The plot displays the Gini coefficient as well as the 'balanced inequality ratio, P'
    (Kunegis and Preusse, doi:10.1145/2380718.238074).
    Parameters:
    xlor, ylor: the cumulative share of the population and measure, respectively (1D);
    x_measure, y_measure: names for the underlying 'subjects' for captioning, e.g.:
      if x is a population of crop patches and y represents their grain yields, then an appropriate
      caption would be had with x_measure='crop patches' and y_measure='grain yields'.
      When x_measure='' (default), x is any population.
    figw: the width or heigth of the square figure.
    show_caption: add a figure caption with a Pareto-rule-like statement using P, such as:
    "P% of the <x_measure> population account for (1-P)% of the <y_measure>."
    save_as: if not '', figure is save.
    """
    # check0:
    try:
        sx = xlor.sum()
        sy = ylor.sum()
    except AttributeError:
        xlor = np.array(xlor)
        ylor = np.array(ylor)
    finally:
        sx = xlor.sum()
        sy = ylor.sum()
        
    # check1:
    N = xlor.size
    if N != ylor.size:
        msg = "The input series must have the same length;"
        msg += "\Given: xlor: {}, ylor: {}.".format(sx,sy)
        raise ValueError(msg)
     
    # check2:
    close_to1 = np.allclose(xlor[-1], 1.0) or np.allclose(ylor[-1], 1.0) 
    if not close_to1:
        msg = "The input series must be the cumulative share of a quantity,"
        msg += " e.g. xlor = x.cumsum()/x.sum()."
        raise TypeError(msg)
        
    if not y_measure: y_measure = 'income';
    
    if figw <= 0: figw = 5
    fig = plt.figure(figsize=(figw + 1, figw))
    ax = fig.add_subplot(111)
    
    alfa = 0.5
    
    # lorenz curve plot:
    ax.plot(xlor, ylor, label='Lorenz')
    
    ax.grid(True, alpha=alfa - 0.3)

    # fill the area between diag, the equality line, and the curve:
    area = plt.fill_between(xlor, xlor, ylor, 
                            color='pink', alpha=alfa - 0.2)

    # Get the gini coef from the fill area, G = 2A.
    twiceA = 1 - 2*np.trapz(ylor, x=xlor)
    ax.text(0.4, 0.15, 'Gini: {:.1%}'.format(twiceA),
            ha='center', fontsize=14)

    # Plot the diagonals:
    # range for diagonals with at least 100 pts:
    Ndx = np.max([100, N])

    dx = np.linspace(0.0, 1.0, Ndx)
    y_anti = 1 - dx 
    
    diag = lines.Line2D(dx, dx, c='green', linestyle='dotted', alpha=alfa);
    anti = lines.Line2D(dx, y_anti, c='grey', linestyle='dotted', alpha=alfa);
    ax.add_line(diag);
    ax.add_line(anti);
    
    # Get the 'balanced inequality ratio', the intersection P of the Lorenz
    # curve with the antidiagonal;
    Px, Py = findIntersection(dx, xlor, ylor, ax=ax)
    
    what = x_measure.center(2+len(x_measure))
    x_pop = 'the{}population '.format(what)
    
    if show_caption:
        # Create a "narrative" to use as caption:
        s = '\n{:.1%} of {} '.format(Py, x_pop)
        s += 'accounts for {:.1%}\n of the {}.'.format(Px, y_measure)
        ax.text(0.5, -0.2, s, ha='center',va='center', fontsize=12);
            
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_title('Lorenz-Gini-P curve ({})'.format(N));
    ax.set_xlabel('Cummuative share of {}'.format(x_pop))
    ax.set_ylabel('Cummuative share of {}'.format(y_measure))
    
    if save_as:
        fname = os.path.basename(save_as).split('.')[0] + '.' + format
        plt.savefig(fname, transparent=True)


def save_file(fname, ext, s, replace=True):
    # check if fname has an extension:
    try:
        i = fname.index('.' , -6)
        outfile = fname[:i] + '.' + 'json'
    except:
        outfile = fname + '.' + 'json'
    
    if replace:
        if os.path.exists(outfile):
            os.remove(outfile)

    if isinstance(s, dict):
        import json

        with open(outfile, 'w') as f:
            f.write(json.dumps(s))
    else:
        if len(s):
            with open(outfile, 'w') as f:
                f.write(s)
    return


def is_lab_notebook():
        import re
        import psutil
        
        return any(re.search('jupyter-lab-script', x)
                   for x in psutil.Process().parent().cmdline())
                   
def check_notebook():
    """
    Util to check a Jupyter notebook environment:
    a markdown cell in a jupyter lab notebook cannot render
    variables: the cell text needs to be created with
    IPython.display.Markdown.
    """

    if is_lab_notebook():
        # need to use Markdown if referencing variables:
        from IPython.display import Markdown
               
        msg = "This is a <span style=\"color:red;\">JupyterLab notebook \
              </span>: Use `IPython.display.Markdown()` if referencing variables; \
              {{var}} does not work."
        return Markdown('### {}'.format(msg))
    

def format_with_bold(s_format):
    """
    Returns the string with all placeholders preceded by '_b' 
    replaced with a bold indicator value (ANSI escape code).
    
    :param: s_format: a string format; 
            if contains '_b{}b_' this term gets bolded.
    :param: s: a string or value
    
    :note 1: '... _b{}; something {}b_ ...' is a valid format.
    :note 2: IndexError is raised using the returned format only when
            the input tuple length < number of placeholders ({});
            it is silent when the later are greater (see Example).
    :TODO: Do same for _f{}f_: to frame a text.
    
    :Example:
    # No error:
    fmt = 'What! _b{}b_; yes: _b{}b_; no: {}.'
    print(format_with_bold(fmt).format('Cat', 'dog', 3, '@no000'))
    # IndexError:
    print(format_with_bold(fmt).format('Cat', 'dog'))
    """

    # Check for paired markers:
    if s_format.count('_b') != s_format.count('b_'):
        err_msg1 = "Bold indicators not paired. Expected '_b{}b_'."
        raise LookupError(err_msg1)
    
    # Check for start bold marker:
    b1 = '_b'
    i = s_format.find(b1 + '{')
    
    # Check marker order: '_b' past 'b_'?:
    if i > s_format.find('}' + 'b_'):
        err_msg2 = "Starting bold indicator not found. Expected '_b{}b_'."
        raise LookupError(err_msg2)
        
    while i != -1:
        
        # Check for trailing bold marker:
        b2 = 'b_'
        j = s_format.find('}' + b2)
        
        if j != -1:
            s_format = s_format.replace(b1, '\033[1m')
            s_format = s_format.replace(b2, '\033[0m')
        else:
            err_msg3 = "Trailing bold indicator not found. Expected '_b{}b_'."
            raise LookupError(err_msg3)
            
        i = s_format.find(b1 + '{')
    
    return s_format


def as_of():
    import datetime
    return datetime.datetime.today().strftime("%b %Y")


def caveat_codor():
    import sys
    from IPython.display import Markdown

    mysys = '{} | {}<br>As of:  {}'.format(sys.version,
                                           sys.platform,
                                           as_of())
    msg = "The code and information herein is valid given my "
    msg += "understanding and this environment:<br>"
    return Markdown(msg + mysys)
