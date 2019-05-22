#!/usr/bin/env python

import sys, os, re, argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

"""
Parse the sampled queue size output file and plot the queue size over time
"""
def parse_qfile(fname, t_min=None, t_max=None):
    fmat = r"(?P<time>[\d.]*) (?P<from_node>[\d]*) (?P<to_node>[\d]*) (?P<q_size_B>[\d.]*) (?P<q_size_p>[\d.]*) (?P<arr_p>[\d.]*) (?P<dep_p>[\d.]*) (?P<drop_p>[\d.]*) (?P<arr_B>[\d.]*) (?P<dep_B>[\d.]*) (?P<drop_B>[\d.]*)"

    time = []
    q_size = []
    with open(fname) as f:
        for line in f:
            searchObj = re.search(fmat, line)
            if searchObj is not None:
                t = float(searchObj.groupdict()['time'])
                if (t_min is not None and t < t_min):
                    continue
                if (t_max is not None and t > t_max):
                    continue
                time.append(t)
                s = float(searchObj.groupdict()['q_size_p'])
                q_size.append(s)
    
    return time, q_size

def parse_namfile(fname, t_min=None, t_max=None):
    total_bytes = 0
    start_time = 0
    with open(fname) as f:
        for line in f:
            split_line = line.split()
            if ((split_line[0] == 'r' and split_line[6] == '1' and
                 split_line[8] == 'tcp')):
                t = float(split_line[2])
                if (t_min is not None and t < t_min):
                    continue
                if (t_max is not None and t > t_max):
                    continue

                # print(line)
                total_bytes += int(split_line[10])
    if t_min is not None:
        start_time = t_min
    if t_max is not None:
        end_time = t_max
    else:
        end_time = t
    return total_bytes * 8 / float(end_time - start_time)

def get_throughputs(fname):
    logs = []
    file = open("log", "w")
    with open(fname) as f:
        for line in f:
            split_line = line.split()
            if ((split_line[0] == 'r' and split_line[6] == '1' and
                 split_line[8] == 'tcp')):
                logs.append(line)
                file.write(line)

        # print(logs)
    num_flows = 5
    throughputs_list =[]
    flows = []
    for i in range(num_flows):
        throughputs_list.append([])
        flows.append(0)

    RUNTIME = 30
    start_time = 0
    splitline = logs[0].split()
    times = np.arange(float(splitline[2]), RUNTIME, 0.1)
    idx = 1
    # print(times)
    end_time = times[idx]
    # import sys
    # sys.exit()
    t1 = []
    for line in logs:
        splitline = line.split()
        s2 = line.split("{")
        time = float(splitline[2])
        # print(time ," ", end_time)
        if time > end_time:
            # do the calculations append flows to throughputs 
            for i, total_bytes in enumerate(flows):
                throughputs_list[i].append(1e-06*((total_bytes * 8 )/0.1))
            # reset flows 
            t1.append(end_time)
            for i, f in enumerate(flows):
                flows[i] = 0
            # modify end time
            idx += 1
            end_time = times[idx]

        byte = int(splitline[10])
        flow = int(s2[1][0])-2
        flows[flow] += (byte)
    
    return throughputs_list, t1      

def config_plot(xlabel, ylabel, title, legend_loc=None):
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.grid()
    plt.legend(loc=legend_loc)

def save_plot(filename, out_dir):    
    plot_filename = os.path.join(out_dir, filename + '.pdf')
    pp = PdfPages(plot_filename)
    pp.savefig()
    pp.close()
    print "Saved plot: ", plot_filename

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--qmon_file", type=str, required=True,
		help="The queue monitor output file")
    parser.add_argument("--out_dir", type=str, default="",
		help="The directory to write output files into")

    try:
        args = parser.parse_args()
    except:
        print >> sys.stderr, "ERROR: failed to parse command line options"
        sys.exit(1)

    # create output directory if it doesn't exist
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    # parse and plot queue size
    time, q_size = parse_qfile(args.qmon_file)
    plt.plot(time, q_size, linestyle='-', marker='o')
    config_plot('time (sec)', 'queue size (packets)', 'Queue Size over Time')
    save_plot('q_size_vs_time', args.out_dir)


if __name__ == "__main__":
    main()

